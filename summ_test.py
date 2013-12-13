# -*- coding: UTF-8 -*-
import sys, os, os.path
import cProfile as profile
import pstats
import math
import logging
import codecs
import itertools
import numpy as np
import gensim
from gensim import models, corpora, similarities, matutils
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import Normalizer
from sklearn.decomposition import TruncatedSVD

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

django_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(13, django_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'pull.settings'

from django.db.models import Count
from django.db.models import Q
from pull.models import *
from cppjiebapy import Tokenize, cut_sentence
from pull.summ import summarize, classify_content, do_classify, load_corpus, summarize4
from pull.summarize import key_rank, sum_rank
from pull.bm25 import BM25, bm25_weights
from pull.textrank import TextRank

dictionary,tfidf_model,lsi_model,sg_class = load_corpus()

def test1():
    obj = HtmlContent.objects.get(pk=46)
    key,sum,cls = summarize(obj.content)
    key2 = key_rank(obj.content)

    sents = list(cut_sentence(obj.content))
    docs = [list(Tokenize(sent)) for sent in sents]
    sum2 = summarize4(sents)

    print 'key1', key, cls
    print 'key2',', '.join(key2)
    print 'sum1',sum
    print 'sum2',sum2

def cos_distance(t):
    (a,b) = t
    dist = np.linalg.norm(a-b)
    #return (1.0 / (1.0+dist) )
    return (0.5+0.5*dist)

def test2():
    obj = HtmlContent.objects.get(pk=34)
    sents = list(cut_sentence(obj.content))
    docs = [dictionary.doc2bow(list(Tokenize(sent))) for sent in sents]
    num_terms = 400
    test_corpus = lsi_model[tfidf_model[docs]]
    #test_sparse = matutils.corpus2csc(test_corpus, num_terms).transpose(copy=False)
    test_dense = matutils.corpus2dense(test_corpus, num_terms).T
    test_a = [a for a in test_dense]
    sim_res = np.fromiter(itertools.imap(cos_distance, itertools.product(test_a,test_a)), dtype=np.float)
    l = len(sents)
    sim_res = np.reshape(sim_res,(l,l))
    print 'lsi=', sim_res

def test3():
    obj = HtmlContent.objects.get(pk=34)
    sents = list(cut_sentence(obj.content))
    docs = [dictionary.doc2bow(list(Tokenize(sent))) for sent in sents]
    bm25 = BM25(docs)
    l = len(sents)
    test_dense = np.zeros((l,l))
    for i in xrange(l):
        scores = bm25.simall(docs[i])
        test_dense[i] = scores
    print 'bm25=', test_dense

def test_rank1(obj):
    sents = list(cut_sentence(obj.content))
    docs = [dictionary.doc2bow(list(Tokenize(sent))) for sent in sents]
    num_terms = 400
    test_corpus = lsi_model[tfidf_model[docs]]
    test_dense = matutils.corpus2dense(test_corpus, num_terms).T
    test_a = [a for a in test_dense]
    sim_res = np.fromiter(itertools.imap(cos_distance, itertools.product(test_a,test_a)), dtype=np.float)
    l = len(sents)
    sim_res = np.reshape(sim_res,(l,l))
    rank = TextRank(sim_res)
    rank.solve()
    top_n_summary = []
    for index in rank.top_index(5):
        top_n_summary.append(sents[index])
    print 'test_rank1 ', u'。 '.join(top_n_summary).replace('\r','').replace('\n','')

def test_rank2(obj):
    sents = list(cut_sentence(obj.content))
    docs = [list(Tokenize(sent)) for sent in sents]
    sim_res = bm25_weights(docs)
    rank = TextRank(sim_res)
    rank.solve()
    top_n_summary = []
    for index in sorted(rank.top_index(3)):
        top_n_summary.append(sents[index])
    return u'。 '.join(top_n_summary).replace('\r','').replace('\n','')+u'。'

def test_rank3(obj):
    sents = list(cut_sentence(obj.content))
    docs = [list(Tokenize(sent)) for sent in sents]
    vect = TfidfVectorizer(min_df=1,tokenizer=Tokenize)
    tfidf = vect.fit_transform(sents)
    lsa = TruncatedSVD(2)
    lsa_res = lsa.fit_transform(tfidf)
    lsa_res = Normalizer(copy=False).fit_transform(lsa_res)
    test_a = [a for a in lsa_res]
    sim_res = np.fromiter(itertools.imap(cos_distance, itertools.product(test_a,test_a)), dtype=np.float)
    l = len(sents)
    sim_res = np.reshape(sim_res,(l,l))
    rank = TextRank(sim_res)
    rank.solve()
    top_n_summary = []
    for index in rank.top_index(5):
        top_n_summary.append(sents[index])
    print 'test_rank1 ', u'。 '.join(top_n_summary).replace('\r','').replace('\n','')

def test4():
    obj = HtmlContent.objects.get(pk=46)
    #test_rank1(obj)
    test_rank2(obj)
    #test_rank3(obj)

def test5():
    for obj in HtmlContent.objects.filter(~Q(content='')):
        sents = list(cut_sentence(obj.content))
        docs = [list(Tokenize(sent)) for sent in sents]
        obj.summerize = summarize4(sents, docs)[0:400]
        obj.save()

#test1()
#test2()
#test3()
#test4()
test5()

'''
prof = profile.Profile()
prof.run('test4()')
stats = pstats.Stats(prof)
stats.strip_dirs().print_stats()
'''
