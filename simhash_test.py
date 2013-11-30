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

import zerorpc
c = zerorpc.Client('tcp://localhost:5678')

def find_duplicate(hashm, hash):
    sims = hashm.find_first(hash)
    #print sims
    return sims[0][1]

def hash_all():
    for obj in HtmlContent.objects.filter(status__lte=2).filter(~Q(content='')):
        #h = long(simhashpy(list(Tokenize(obj.content)), 64))
        h = simhash.hash_token(list(Tokenize(obj.content)))
        obj.hash = h
        if find_duplicate(c, h) == 0:
            obj.status = 0
        else:
            obj.status = 1
            #obj.hash = (hash(obj.url) & 0xFFFFFFFF)
        #obj.save(force_update=True, update_fields=['hash', 'status'])
        obj.save()
        c.insert(h)
#hash_all()

#print find_duplicate(c,2380402939662658583)
obj1 = HtmlContent.objects.get(hash=3262982581)
h1 = simhash.hash_token(list(Tokenize(obj1.content)))
print c.find_all(h1)
#h1 = simhashpy(list(Tokenize(obj1.content)))
#h2 = 11128035827389547469
#obj2 = HtmlContent.objects.get(hash=11128035827389547469)
#h2 = simhashpy(list(Tokenize(obj2.content)))

#print corpus.distance(h1,h2)
#print h1.hamming_distance(h2)
#print c.find_all(h1)
#print find_duplicate(c,6)

'''
obj1 = HtmlContent.objects.get(hash=2633880672150661580)
obj2 = HtmlContent.objects.get(hash=2642887871407499724)
print obj1.url,obj2.url
token1 = list(Tokenize(obj1.content))
token2 = list(Tokenize(obj2.content))
h1 = simhashpy(token1, 64)
h2 = simhashpy(token2, 64)
print h1,h2
print h1.similarity(h2)
print h1.hamming_distance(h2)
print corpus.distance(h1,h2)

h1 = simhash.hash_token(token1)
h2 = simhash.hash_token(token2)
print corpus.distance(h1,h2)
'''
