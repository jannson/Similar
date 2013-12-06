# -*- coding: UTF-8 -*-
import sys, os
import numpy as np
from hashes.simhash import simhash as simhashpy
from hashes.nilsimsa import nilsimsa
from sklearn.metrics.pairwise import pairwise_distances as sk_pd

import simhash

corpus = simhash.Corpus(6,3)

def hashdistance(str1, str2):
    hash1 = simhashpy(str1, 64)
    hash2 = simhashpy(str2, 64)

    #distance = 1 - hash1.similarity(hash2)
    #return hash1.similarity(hash2)
    print hash1, hash2
    print hash1.hamming_distance(hash2)
    print corpus.distance(hash1,hash2)
    corpus.insert(hash1)
    corpus.insert(hash2)
    print corpus.find_all(hash1)
    #return distance
    
strings = ['n some cases it’s useful to restrict the number of features. CountVectorizer has a'
        , ' CountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabulary'
        , ' CountVectorizer has a  constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits th has a max_features constructor that limits the vocabul']

#hashdistance(strings[1], strings[2])

django_path = '/opt/projects/git_source/Similar'
sys.path.insert(13, django_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'pull.settings'

from django.db.models import Count
from django.db.models import Q
from pull.models import *

from cppjiebapy import Tokenize
from hashes.simhash import simhash as simhashpy
#import dse
#dse.patch_models(specific_models=[HtmlContent])
from bulkops import update_many
import Pyro4

import zerorpc
c = zerorpc.Client('tcp://localhost:5678')

def find_duplicate(hashm, hash):
    sims = hashm.find_first(hash)
    #print sims
    return sims[0][1]

def hash_all():
    for obj in HtmlContent.objects.filter(status__lte=2).filter(~Q(content='')):
        h = simhash.hash_tokenpy(list(Tokenize(obj.content)))
        if find_duplicate(c, h) == 0:
            obj.status = 0
        else:
            obj.status = 1
        obj.hash = h
        obj.save()
        c.insert(h)
#hash_all()

def hash_test():
    sim_server = Pyro4.Proxy(Pyro4.locateNS().lookup('gensim.testserver'))
    dels = []
    for obj in HtmlContent.objects.filter(status=1).filter(~Q(content='')):
        dels.append('html_%d' % obj.id)
    sim_server.delete(dels)
hash_test()

obj1 = HtmlContent.objects.get(pk=4815)
obj2 = HtmlContent.objects.get(pk=4817)
token1 = list(Tokenize(obj1.content))
token2 = list(Tokenize(obj2.content))
h1 = simhashpy(token1, 64)
h2 = simhashpy(token2, 64)
print h1,h2
print corpus.distance(h1,h2)
h1 = simhash.hash_token(token1)
h2 = simhash.hash_token(token2)
print h1,h2
print corpus.distance(h1,h2)
h1 = simhash.hash_tokenpy(token1)
h2 = simhash.hash_tokenpy(token2)
print h1,h2
print corpus.distance(h1,h2)

'''
str1 = 'test love you'
str2 = 'love you test'
t1 = str1.decode('utf-8').split()
t2 = str2.decode('utf-8').split()
h1 = simhash.hash_token(t1)
h2 = simhash.hash_token(t2)
h2 = simhash.hash_token(t1)
print h1,h2
print corpus.distance(h1,h2)
'''
