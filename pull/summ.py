# -*- coding: UTF-8 -*-
import sys, os, os.path, codecs, math
import logging
from scipy.odr import models
import unittest
import os
import os.path
import tempfile
import logging

import numpy as np
from sklearn.linear_model import SGDClassifier

import gensim
from gensim.corpora import mmcorpus, Dictionary
from gensim.models import lsimodel, ldamodel, tfidfmodel, rpmodel, logentropy_model, TfidfModel, LsiModel
from gensim import matutils,corpora

import cppjiebapy
from cppjiebapy import Tokenize

import gensim
from gensim import models, corpora, similarities
import Pyro4
from simserver import SessionServer

from pull.models import *

#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

#print sys.getdefaultencoding()

copus_path = '/opt/projects/packages/sougou_corpus'
#copus_path = '/home/gan/download/sogou_copus'
HERE = os.path.dirname(os.path.abspath(__file__))



class MyCorpus(object):
    def __init__(self):
        self.cls_init = False
        self.cls_y = []
        self.cls_ids = {}
        self.ids_cls = {}
        self.cls = {}

        cls_file = os.path.join(copus_path, 'ClassList.txt')
        cls_i = 0
        with open(cls_file) as file:
            content = file.read().decode('gb2312').encode('utf-8').decode('utf-8')
            for l in content.split('\n'):
                cs = l.split()
                if len(cs) > 1:
                    self.cls[cs[0]] = cs[1]
                    self.ids_cls[cls_i] = cs[1]
                    self.cls_ids[cs[1]] = cls_i
                    cls_i += 1

        self.dictionary = gensim.corpora.Dictionary(self.iter_documents())
        self.dictionary.filter_extremes(no_below=1, keep_n=20000) # check API docs for pruning params
        #self.dictionary.save_as_text('sogou_dic.txt')

    def iter_files(self):
        copus_sample = os.path.join(copus_path, 'Sample')
        for d in os.listdir(copus_sample):
            d1 = os.path.join(copus_sample, d)
            if os.path.isdir(d1):
                for d3 in os.listdir(d1):
                    f = os.path.join(d1, d3)
                    if os.path.isfile(f):
                        if not self.cls_init:
                            self.cls_y.append(self.cls_ids[self.cls[d]])
                        yield self.cls[d],f
        self.cls_init = True

    def iter_documents(self):
        for c,f in self.iter_files():
            with open(f) as file:
                content = file.read().decode('gb2312', 'ignore').encode('utf-8').decode('utf-8', 'replace')
                yield [s for s in Tokenize(content)]

    def __iter__(self):
        for tokens in self.iter_documents():
            yield self.dictionary.doc2bow(tokens)

def make_corpus():
    corpus = MyCorpus()
    tfidf_model = TfidfModel(corpus)
    #corpora.MmCorpus.serialize('wiki_en_corpus.mm', corpus) # store to disk, for later use
    corpus.dictionary.save(os.path.join(HERE, 'sogou.dict')) # store the dictionary, for future reference
    tfidf_model.save(os.path.join(HERE, 'sogou.model'))

def load_corpus():
    dictionary = corpora.Dictionary.load(os.path.join(HERE,'sogou.dict'))
    tfidf_model = tfidfmodel.TfidfModel.load(os.path.join(HERE, 'sogou.model'))
    return dictionary, tfidf_model

def do_classify():
    corpus = MyCorpus()
    tfidf_model = TfidfModel(corpus)
    corpus_idf = tfidf_model[corpus]
    num_terms = len(corpus.dictionary)
    corpus_sparse = matutils.corpus2csc(corpus_idf, num_terms).transpose(copy=False)
    #print corpus_sparse.shape
    #corpus_dense = matutils.corpus2dense(corpus_idf, len(corpus.dictionary))
    #print corpus_dense.shape
    clf = SGDClassifier(loss='modified_huber')
    y = np.array(corpus.cls_y)
    #print y.shape
    clf.fit(corpus_sparse, y)

    with open(os.path.join(copus_path, 'Sample/C000007/10.txt')) as file:
        content = file.read().decode('gb2312', 'ignore').encode('utf-8').decode('utf-8', 'replace')
        test_corpus = tfidf_model[corpus.dictionary.doc2bow([s for s in Tokenize(content[300:1000])])]
        test_sparse = matutils.corpus2csc([test_corpus], num_terms).transpose(copy=False)
        #print corpus.ids_cls[clf.predict(test_sparse)[0]], corpus.cls['C000007']
        print clf.predict_proba(test_sparse)

#make_corpus()
#do_classify()
dictionary,tfidf_model = load_corpus()
def key_words(content, topk=18):
    vec_bow = dictionary.doc2bow([s for s in Tokenize(content)])
    tfidf_corpus = tfidf_model[vec_bow]
    return [dictionary[d].decode('utf-8') for d,_ in sorted(list(tfidf_corpus), key=lambda item:-item[1])[0:topk]]

CLUSTER_THRESHOLD = 5  # Distance between words to consider
TOP_SENTENCES = 8  # Number of sentences to return for a "top n" summary

def __score_sentences(sentences, important_words):
    scores = []
    sentence_idx = -1

    for s in [list(cppjiebapy.cut(s)) for s in sentences]:
        sentence_idx += 1
        word_idx = []

        # For each word in the word list...
        for w in important_words:
            try:
                # Compute an index for where any important words occur in the sentence
                word_idx.append(s.index(w))
            except ValueError, e: # w not in this particular sentence
                pass

        word_idx.sort()

        # It is possible that some sentences may not contain any important words at all
        if len(word_idx)== 0: continue

        # Using the word index, compute clusters by using a max distance threshold
        # for any two consecutive words

        clusters = []
        cluster = [word_idx[0]]
        i = 1
        while i < len(word_idx):
            if word_idx[i] - word_idx[i - 1] < CLUSTER_THRESHOLD:
                cluster.append(word_idx[i])
            else:
                clusters.append(cluster[:])
                cluster = [word_idx[i]]
            i += 1
        clusters.append(cluster)

        # Score each cluster. The max score for any given cluster is the score 
        # for the sentence

        max_cluster_score = 0
        for c in clusters:
            significant_words_in_cluster = len(c)
            total_words_in_cluster = c[-1] - c[0] + 1
            score = 1.0 * significant_words_in_cluster \
                * significant_words_in_cluster / total_words_in_cluster

            if score > max_cluster_score:
                max_cluster_score = score

        scores.append((sentence_idx, score))
    return scores

N_2 = 68  # Number of words to consider
def summarize(txt):
    sentences = []
    for s in cppjiebapy.cut_sentence(txt):
        sentences.append(s.lower())
    normalized_sentences = [s.lower() for s in sentences]

    top_n_words = key_words(txt, N_2)
    scored_sentences = __score_sentences(sentences, top_n_words)

    top_n_scored = sorted(scored_sentences, key=lambda s: s[1])[-TOP_SENTENCES:]
    top_n_scored = sorted(top_n_scored, key=lambda s: s[0])
    top_n_summary=[sentences[idx] for (idx, score) in top_n_scored]
    return ', '.join(top_n_words[:18]), u'。 '.join(top_n_summary) + u'。'

def summarize2(txt):
    return summarize(txt)[1]

def _mean_std(l):
    ln = len(l)
    if ln <= 0:
        return (0.0,0.0)
    mean = sum(l,0.0)/ln
    d = [(i-mean)**2 for i in l]
    std_dev = math.sqrt(sum(d)/len(d))
    return (mean, std_dev)

N_3 = 80  # Number of words to consider
def summarize3(txt):
    sentences = []
    for s in cppjiebapy.cut_sentence(txt):
        sentences.append(s.lower())
    normalized_sentences = [s.lower() for s in sentences]

    top_n_words = key_words(txt, N_3)
    scored_sentences = __score_sentences(normalized_sentences, top_n_words)
    avg_list = [s[1] for s in scored_sentences]
    avg = np.mean(avg_list)
    std = np.std(avg_list)
    #avg,std = _mean_std([s[1] for s in scored_sentences])
    mean_scored = [(sent_idx, score) for (sent_idx, score) in scored_sentences
                   if score > avg + 0.5 * std]
    mean_scored_summary=[sentences[idx] for (idx, score) in mean_scored]
    return u'。 '.join(mean_scored_summary) + u'。 '

#server = SessionServer('/tmp/server')
server = Pyro4.Proxy(Pyro4.locateNS().lookup('gensim.testserver'))
def sim_search(content):
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

def sim_index(obj):
    doc = {}
    doc['id'] = 'html_%d' % obj.id
    doc['tokens'] = [s for s in Tokenize(obj.content)]
    server.index([doc])

def test():
    with open(os.path.join(copus_path, 'Sample/C000007/10.txt')) as file:
        content = file.read().decode('gb2312', 'ignore').encode('utf-8').decode('utf-8', 'replace')
        #print ' '.join(key_words(content))
        #print summarize2(content)
        #print summarize3(content)

#test()
