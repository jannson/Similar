# -*- coding: UTF-8 -*-
import sys, os, os.path

HERE = os.path.dirname(os.path.abspath(__file__))

root_path = os.path.join(HERE,'pull')
sys.path.insert(13, root_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'pull.settings'

from django.db.models import Count
from django.db.models import Q
from pull.models import *

from django.utils.encoding import force_unicode
import codecs

import yaha
from yaha.analyse import ChineseAnalyzer 

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        from django.utils import simplejson as json

try:
    import whoosh
except ImportError:
    raise MissingDependency("The 'whoosh' backend requires the installation of 'Whoosh'. Please refer to the documentation.")

# Bubble up the correct error.
from whoosh.fields import Schema, IDLIST, STORED, TEXT, KEYWORD, NUMERIC, BOOLEAN, DATETIME, NGRAM, NGRAMWORDS
from whoosh.fields import ID as WHOOSH_ID
from whoosh import index, query, sorting, scoring
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.filedb.filestore import FileStorage, RamStorage
from whoosh.searching import ResultsPage
from whoosh.writing import AsyncWriter

def _from_python(value):
    """
    Converts Python values to a string for Whoosh.

    Code courtesy of pysolr.
    """
    if hasattr(value, 'strftime'):
        if not hasattr(value, 'hour'):
            value = datetime(value.year, value.month, value.day, 0, 0, 0)
    elif isinstance(value, bool):
        if value:
            value = 'true'
        else:
            value = 'false'
    elif isinstance(value, (list, tuple)):
        value = u','.join([force_unicode(v) for v in value])
    elif isinstance(value, (int, long, float)):
        # Leave it alone.
        pass
    else:
        value = force_unicode(value)
    return value

use_file_storage = True
content_field_name = 'content'
def schema_init():
    storage = None
    key_path = 'key_index'
    if use_file_storage and not os.path.exists(key_path):
        os.mkdir(key_path)
    storage = FileStorage(key_path)
    schema_fields = {
            'id': WHOOSH_ID(stored=True, unique=True),
    }

    schema_fields['title'] = TEXT(stored=True, analyzer=ChineseAnalyzer())
    schema_fields['content'] = TEXT(stored=True, analyzer=ChineseAnalyzer(), vector=True)
    schema = Schema(**schema_fields)
    return (storage, schema)

def write_db(storage,schema):
    index = storage.create_index(schema)
    writer = index.writer()
        
    #for dou in DoubanMovie.objects.filter(id__lte=4000).annotate(cnt=Count('movielink')).filter(cnt__gt=0).order_by('-cnt'):
    for obj in HtmlContent.objects.filter(~Q(retry=3)).filter(~Q(content='')):
        doc = {}
        doc['id'] = _from_python(str(obj.id))
        doc['title'] = obj.title
        doc['content'] = obj.content
        try:
            writer.update_document(**doc)
        except Exception, e:
            raise

    writer.commit()
    print 'write_db finished'

def search_db(storage, schema):
    index = storage.open_index(schema=schema)
    searcher = index.searcher()
    parser = QueryParser(content_field_name, schema=schema)
    parsed_query = parser.parse('2020')
    raw_results = searcher.search(parsed_query)
    for hit in raw_results:  
        print hit.highlights(content_field_name)

import numpy as np
import scipy.linalg as lin
from sklearn.cluster import KMeans, AffinityPropagation
import itertools

def key_terms(storage, schema):
    index = storage.open_index(schema=schema)
    ixreader = index.reader()
    searcher = index.searcher()
    docnums = []
    KEY_LEN = 500
    DOC_LEN = 1000
    for id in xrange(DOC_LEN):
        docnums.append(id)
    #for id in ixreader.all_doc_ids():
    #    print id,
    terms = {}
    i = 0
    for term,score in searcher.key_terms(docnums, content_field_name, KEY_LEN):
        terms[term] = i
        i += 1
    print 'key_terms finished'

    ar = np.zeros( (len(docnums), KEY_LEN) )
    for i in xrange(DOC_LEN):
        term_weights = ixreader.vector_as("weight", i, content_field_name)
        all_weight = 0
        n = 0
        for term,weight in term_weights:
            if term in terms:
                ar[i][terms[term]] = weight
                all_weight += weight
                n += 1
        for j in xrange(KEY_LEN):
            ar[i][j] = ar[i][j]/weight
    
    u,s,v = lin.svd(ar, full_matrices=False)
    data = u[:,0:100]
    print 'svd finished'

    k = KMeans(init='k-means++', n_init=10)
    k.fit(data)
    #centroids = k.cluster_centers_
    labels = k.labels_
    print 'kmeans finished'

    #af = AffinityPropagation(affinity="euclidean").fit(data)
    #cluster_centers_indices = af.cluster_centers_indices_
    #labels = af.labels_
    
    doc_arr = np.array(range(DOC_LEN))
    for i in range(np.max(labels)):
        print 'group:', (i+1)
        for doc_num in doc_arr[labels==i]:
            print ixreader.stored_fields(doc_num).get('id'), ixreader.stored_fields(doc_num).get('title').split('|')[0]+ '/',
        print '\n'

    #print ixreader.stored_fields(1).get(content_field_name)

def test():
    storage,schema = schema_init()

    #write_db(storage, schema)
    #search_db(storage, schema)
    key_terms(storage, schema)

test()

