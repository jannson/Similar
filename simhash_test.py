# -*- coding: UTF-8 -*-
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
    print hash1.hamming_distance(hash2)
    print corpus.distance(hash1,hash2)
    corpus.insert(hash1)
    corpus.insert(hash2)
    print corpus.find_all(hash1)
    #return distance
    
strings = ['n some cases it’s useful to restrict the number of features. CountVectorizer has a'
        , ' CountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabulary'
        , ' CountVectorizer has a  constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits the vocabularyCountVectorizer has a max_features constructor argument that limits th has a max_features constructor that limits the vocabul']

hashdistance(strings[1], strings[2])
