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
import Pyro4

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

django_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(13, django_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'pull.settings'

from django.db.models import Count
from django.db.models import Q
from pull.models import *
from cppjiebapy import Tokenize
from pull.summ import summarize, classify_content, do_classify, save_corpus, make_corpus, classify_vector_test

def iter_documents():
    """Iterate over all documents, yielding a document (=list of utf8 tokens) at a time."""
    for obj in HtmlContent.objects.filter(status=0).filter(~Q(content='')):
        doc = {}
        doc['id'] = 'html_%d' % obj.id
        doc['tokens'] = list(Tokenize(obj.content))
        if obj.id % 1000 == 0:
            print 'processing', obj.id
        yield doc

def iter_corpus():
    for obj in SogouCorpus.objects.all():
        doc = {}
        doc['id'] = 'sogou_%d' % obj.id
        doc['tokens'] = obj.tokens.split(',')
        if obj.id % 1000 == 0:
            print 'processing', obj.id
        yield doc

server = SessionServer('/tmp/server')
#server = Pyro4.Proxy(Pyro4.locateNS().lookup('gensim.testserver'))
def train_server():
    training_corpus = iter_documents()
    #training_corpus = iter_corpus()
    #server.train(list(training_corpus), method='lsi')
    #print 'train finished'
    server.index(training_corpus)
    print 'index finished'
    server.optimize()
    print 'optimize finished'

def update_keywords():
    for html in HtmlContent.objects.filter(~Q(retry=3)).filter(~Q(content='')):
        html.tags,html.summerize = summarize(html.content)
        html.summerize = html.summerize[0:388]
        html.save()

def reset_ids():
    ids = []
    for obj in HtmlContent.objects.filter(status=0).filter(~Q(content='')):
        ids.append(obj.id)
    ids_set = frozenset(ids)
    ids_del = []
    for id in range(3000):
        if id not in ids_set:
            ids_del.append('html_%d' % id)
    server.delete(ids_del)

#update_keywords()
train_server()
#reset_ids()

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

def search2(doc):
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

#save_corpus()
#make_corpus()
#do_classify()
#content = u'市国税局推出推进出口货物跨部门合作机制'
#for v,score in search2('html_6769'):
#    print "%s(%f) / " % (v.title.split('|')[0],score),
#obj = HtmlContent.objects.get(pk=524)
#print classify_content(content)
#for v,score in search(obj.content):
#    print "%s(%f) / " % (v.title.split('|')[0],score),

classify_vector_test()
