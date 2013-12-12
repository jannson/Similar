# -*- coding: UTF-8 -*-
import sys, os, os.path
import logging
import gensim
from gensim import models, corpora, similarities, matutils
import codecs

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

django_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(13, django_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'pull.settings'

from django.db.models import Count
from django.db.models import Q
from pull.models import *
from cppjiebapy import Tokenize
from pull.summ import summarize, classify_content, do_classify, load_corpus
from pull.summarize import key_rank, sum_rank
from pull.bm25 import BM25

dictionary,tfidf_model,lsi_model,sg_class = load_corpus()

def test1():
    obj = HtmlContent.objects.get(pk=34)
    key,sum,cls = summarize(obj.content)
    key2 = key_rank(obj.content)
    sum2 = sum_rank(obj.content)

    print 'key1', key
    print 'key2',', '.join(key2)
    print 'sum1',sum
    print 'sum2',sum2

def test2():
    obj = HtmlContent.objects.get(pk=34)
    sents = list(cut_sentence(text))
    docs = [dictionary.doc2bow(list(Tokenize(sent))) for sent in sents]
    sims = lsi_model[tfidf_model[docs]]
    num_terms = 400
    test_sparse = matutils.corpus2csc([test_corpus], num_terms).transpose(copy=False)
    print test_sparse.T

test2()

