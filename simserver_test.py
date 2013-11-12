# -*- coding: UTF-8 -*-
import sys, os, os.path
import logging
import pprint
from collections import defaultdict
import json
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster, ward
from sklearn.cluster.affinity_propagation_ import affinity_propagation
from sklearn.cluster import KMeans
import gensim
from gensim import models, corpora, similarities
import codecs

from cppjiebapy import Tokenize
from simserver import SessionServer

django_path = '/home/gan/project/source/svn_project/pull/1'
sys.path.insert(13, django_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'pull.settings'

from django.db.models import Count
from django.db.models import Q
from pull.models import *
from cppjiebapy import Tokenize

def iter_documents():
    """Iterate over all documents, yielding a document (=list of utf8 tokens) at a time."""
    for obj in HtmlContent.objects.filter(~Q(retry=3)).filter(~Q(content='')):
        doc = {}
        doc['id'] = 'html_%d' % obj.id
        doc['tokens'] = [s for s in Tokenize(obj.title)]*3 + [s for s in Tokenize(obj.content)]
        yield doc

server = SessionServer('/tmp/server')
#training_corpus = list(iter_documents())
#server.train(training_corpus, method='lsi')
print 'train finished'
#server.index(training_corpus)
print 'index finished'
#server.commit()

obj = HtmlContent.objects.filter(~Q(retry=3)).filter(~Q(content=''))[0]
doc = {}
#content = obj.content[50:100]
print obj.content[50:100]
content = 'Google facebook 深圳'
print content
doc['tokens'] = [s for s in Tokenize(content)]
for result in server.find_similar(doc):
    id = int(result[0].split('_')[1])
    obj = HtmlContent.objects.get(pk=id)
    print "%s(%f) / " % (obj.title.split('|')[0],result[1]),
