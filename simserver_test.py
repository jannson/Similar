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

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

django_path = os.path.dirname(os.path.abspath(__file__))
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
training_corpus = iter_documents()
server.train(training_corpus, method='lsi')
print 'train finished'
#server.index(training_corpus)
#print 'index finished'
#server.commit()

def search(content):
    doc = {}
    doc['tokens'] = [s for s in Tokenize(content)]
    model_pks = []
    scores = []
    for result in server.find_similar(doc):
        id = int(result[0].split('_')[1])
        model_pks.append(id)
        scores.append(result[1])
    objs = []
    bulk_objs = HtmlContent.objects.in_bulk(model_pks)
    for k,v in enumerate(model_pks):
        objs.append((bulk_objs[v],scores[k]))

    return objs

content = u'市国税局推出推进出口货物跨部门合作机制'
for v,score in search(content):
    print "%s(%f) / " % (v.title.split('|')[0],score),

'''class SearchQuerySet(object):
    def __init__(self, content):
    def __len__(self):
    def __iter__(self):
    def __getitem__(self, k):
    def count(self):
        return len(self)'''
