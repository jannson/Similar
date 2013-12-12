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
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import SGDClassifier
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.preprocessing import Normalizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.externals import joblib
from sklearn import metrics

import gensim
from gensim.corpora import mmcorpus, Dictionary
from gensim.models import tfidfmodel, TfidfModel, LsiModel
from gensim import matutils,corpora

import cppjiebapy
from cppjiebapy import Tokenize

import gensim
from gensim import models, corpora, similarities
import Pyro4
import zerorpc

from django.conf import settings
from pull.models import *

#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

#print sys.getdefaultencoding()

copus_path = settings.COPUS_PATH
HERE = os.path.dirname(os.path.abspath(__file__))

def load_corpus():
    dictionary = corpora.Dictionary.load(os.path.join(HERE,'sogou.dict'))
    tfidf_model = tfidfmodel.TfidfModel.load(os.path.join(HERE, 'sogou.model'))
    lsi_model = LsiModel.load(os.path.join(HERE, 'sogou.lsi'))
    try:
        sg_class = joblib.load(os.path.join(HERE, 'sgdc_clf.pkl'))
    except:
        sg_class = None
    return dictionary, tfidf_model, lsi_model, sg_class

def load_class_ids():
    cls_file = os.path.join(copus_path, 'ClassList.txt')
    cls_i = 0
    ids_cls = {}
    cls_ids = {}
    with open(cls_file) as file:
        content = file.read().decode('gb2312').encode('utf-8').decode('utf-8')
        for l in content.split('\n'):
            cs = l.split()
            if len(cs) > 1:
                ids_cls[cls_i] = cs[1]
                cls_ids[cs[1]] = cls_i
                cls_i += 1
    return ids_cls,cls_ids

dictionary,tfidf_model,lsi_model,sg_class = load_corpus()
id2cls,cls_ids = load_class_ids()

def id2cls_func(id):
    return id2cls[id]

class MyCorpus(object):
    def __init__(self):
        self.cls_init = False
        self.train_cnt = 17000
        self.cls_y = []
        self.cls_ids = {}
        self.ids_cls = {}
        self.cls = {}
        self.test_y = list(np.random.randint(0, self.train_cnt, 4000))

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

        #self.dictionary = gensim.corpora.Dictionary(self.iter_tokens())
        #self.dictionary.filter_extremes(no_below=1, keep_n=20000) # check API docs for pruning params
        #self.dictionary.save_as_text('sogou_dic.txt')
        self.dictionary = dictionary

    def iter_files(self):
        copus_sample = os.path.join(copus_path, 'Sample')
        for d in os.listdir(copus_sample):
            d1 = os.path.join(copus_sample, d)
            if os.path.isdir(d1):
                for d3 in os.listdir(d1):
                    f = os.path.join(d1, d3)
                    if os.path.isfile(f):
                        #if not self.cls_init:
                        #    self.cls_y.append(self.cls_ids[self.cls[d]])
                        yield self.cls[d],f
        #self.cls_init = True

    def save_to_db(self):
        corpus_db = []
        cnt = 0
        for c,f in self.iter_files():
            corpus = SogouCorpus()
            with open(f) as file:
                content = file.read().decode('gb2312', 'ignore').encode('utf-8').decode('utf-8', 'replace')
                corpus.content = content
                corpus.tokens = ','.join([s for s in Tokenize(content)])
                corpus.classify = c
                corpus_db.append(corpus)
                cnt += 1
                if cnt % 80 == 0:
                    print '#',
                    error = False
                    try:
                        SogouCorpus.objects.bulk_create(corpus_db)
                    except:
                        error = True
                    if error:
                        for cor in corpus_db:
                            cor.save()
                    corpus_db = []
        if len(corpus_db) > 0:
            error = False
            try:
                SogouCorpus.objects.bulk_create(corpus_db)
            except:
                error = True
            if error:
                for cor in corpus_db:
                    cor.save()
            corpus_db = []
        print 'complete'
    
    def iter_documents_y(self):
        for obj in SogouCorpus.objects.exclude(id__in=self.test_y):
            self.cls_y.append(cls_ids[obj.classify])
            yield obj.tokens
        self.cls_init = True

    def iter_documents(self):
        for obj in SogouCorpus.objects.exclude(id__in=self.test_y):
            yield obj.tokens

    def iter_tokens(self):
        for tokens in self.iter_doc():
            yield tokens.split(',')

    def iter_doc(self):
        if self.cls_init:
            iters = self.iter_documents
        else:
            iters = self.iter_documents_y
        for t in iters():
            yield t

    def __iter__(self):
        for tokens in self.iter_doc():
            yield self.dictionary.doc2bow(tokens.split(','))

def save_corpus():
    corpus = MyCorpus()
    corpus.save_to_db()

def make_corpus():
    corpus = MyCorpus()
    tfidf_model = TfidfModel(corpus)
    corpus_idf = tfidf_model[corpus]
    num_terms = 400
    lsi_model = LsiModel(corpus_idf, id2word=corpus.dictionary, num_topics=num_terms)
    #corpora.MmCorpus.serialize('wiki_en_corpus.mm', corpus) # store to disk, for later use
    corpus.dictionary.save(os.path.join(HERE, 'sogou.dict')) # store the dictionary, for future reference
    tfidf_model.save(os.path.join(HERE, 'sogou.model'))
    lsi_model.save(os.path.join(HERE, 'sogou.lsi'))
    print 'save dictionary and tfidf model'
    '''    
    corpus_lsi = lsi_model[corpus_idf]
    #num_terms = len(corpus.dictionary)
    corpus_sparse = matutils.corpus2csc(corpus_lsi, num_terms).transpose(copy=False)
    #print corpus_sparse.shape
    #corpus_dense = matutils.corpus2dense(corpus_idf, len(corpus.dictionary))
    #print corpus_dense.shape
    #clf = SGDClassifier(loss='modified_huber')
    clf = SGDClassifier(loss='hinge')
    y = np.array(corpus.cls_y)
    #print y.shape
    clf.fit(corpus_sparse, y)
    filename = os.path.join(HERE, 'sgdc_clf.pkl')
    _ = joblib.dump(clf, filename, compress=9)
    '''

def do_classify():
    corpus = MyCorpus()
    #tfidf_model = TfidfModel(corpus)
    corpus_idf = tfidf_model[corpus]
    #corpus_lsi = lsi_model[corpus_idf]
    num_terms = len(corpus.dictionary)
    #num_terms = 400
    corpus_sparse = matutils.corpus2csc(corpus_idf, num_terms).transpose(copy=False)
    #print corpus_sparse.shape
    #corpus_dense = matutils.corpus2dense(corpus_idf, len(corpus.dictionary))
    #print corpus_dense.shape
    penalty = 'l2'
    clf = SGDClassifier(loss='hinge', penalty=penalty, alpha=0.0001, n_iter=50, fit_intercept=True)
    #clf = LinearSVC(loss='l2', penalty=penalty, dual=False, tol=1e-3)
    y = np.array(corpus.cls_y)
    #print y.shape
    clf.fit(corpus_sparse, y)
    filename = os.path.join(HERE, 'sgdc_clf.pkl')
    _ = joblib.dump(clf, filename, compress=9)
    print 'train completely'

    X_test = []
    X_label = []
    for obj in SogouCorpus.objects.filter(id__in=corpus.test_y):
        X_test.append(obj.tokens)
        X_label.append(cls_ids[obj.classify])
        #result = classifier.predict(obj.tokens)
    test_corpus = [dictionary.doc2bow(s.split(',')) for s in X_test]
    test_corpus = tfidf_model[test_corpus]
    test_corpus = matutils.corpus2csc(test_corpus, num_terms).transpose(copy=False)
    pred = clf.predict(test_corpus)
    score = metrics.f1_score(X_label, pred)
    print("f1-score:   %0.3f" % score)

def classify_content(content):
    num_terms = len(dictionary)
    test_corpus = tfidf_model[dictionary.doc2bow(list(Tokenize(content)))]
    test_sparse = matutils.corpus2csc([test_corpus], num_terms).transpose(copy=False)
    result = sg_class.predict(test_sparse)
    return id2cls[result[0]]
    #return zip(id2cls.values(),result)

def sklearn_test():
    tok = lambda (x): x.split(',')
    '''
    classifier = Pipeline([
        ('vectorizer', CountVectorizer(tokenizer=tok)),
        ('tfidf', TfidfTransformer()),
        ('chi', SelectKBest(chi2, k=120)),
        ('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=0.00001, n_iter=50, fit_intercept=True))])
    '''

    corpus = MyCorpus()
    X_train = list(corpus.iter_doc())
    Y_train = corpus.cls_y

    #vectorizer = HashingVectorizer(tokenizer=tok, non_negative=True, n_features=2**16)
    #X_train = vectorizer.transform(X_train)
    hasher = HashingVectorizer(n_features=2**16,
                               tokenizer=tok, non_negative=True,
                               norm=None, binary=False)
    vectorizer = Pipeline((
        ('hasher', hasher),
        ('tf_idf', TfidfTransformer())
    ))
    #vectorizer = TfidfVectorizer(tokenizer=tok, sublinear_tf=True, max_df=0.5)
    X_train = vectorizer.fit_transform(X_train)
    #ch2 = SelectKBest(chi2, k=400)
    #X_train = ch2.fit_transform(X_train, Y_train)
    #lsa = TruncatedSVD(400)
    #X_train = lsa.fit_transform(X_train)
    #X_train = Normalizer(copy=False).fit_transform(X_train)
    clf = SGDClassifier(loss='hinge', penalty='l2', alpha=0.00001, n_iter=50, fit_intercept=True)
    #clf = MultinomialNB(alpha=.01)
    clf.fit(X_train, Y_train)
    print 'train completely'
    
    X_test = []
    X_label = []
    for obj in SogouCorpus.objects.filter(id__in=corpus.test_y):
        X_test.append(obj.tokens)
        X_label.append(cls_ids[obj.classify])
        #result = classifier.predict(obj.tokens)
    X_test = vectorizer.transform(X_test)
    #X_test = ch2.transform(X_test)
    #X_test = lsa.transform(X_test)
    #X_test = Normalizer(copy=False).transform(X_test)
    pred = clf.predict(X_test)
    score = metrics.f1_score(X_label, pred)
    print("f1-score:   %0.3f" % score)
    '''
    i = 0
    for n,id in enumerate(X_label):
        if id != pred[n]:
            print "(%d,%s,%s)" % (n,id2cls[pred[n]],id2cls[id]),
            i += 1
            if i % 18 == 0:
                print ''
    print 'error num=',i
    '''

#make_corpus()
#do_classify()
# TODO do better for this
def key_words(content, topk=18):
    vec_bow = dictionary.doc2bow([s for s in Tokenize(content)])
    tfidf_corpus = tfidf_model[vec_bow]

    num_terms = len(dictionary)
    test_sparse = matutils.corpus2csc([tfidf_corpus], num_terms).transpose(copy=False)
    result = sg_class.predict(test_sparse)

    words = [dictionary[d].decode('utf-8') for d,_ in sorted(list(tfidf_corpus), key=lambda item:-item[1])[0:topk]]
    classify = id2cls[result[0]]

    return (words,classify)

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

    (top_n_words,cls) = key_words(txt, N_2)
    scored_sentences = __score_sentences(sentences, top_n_words)

    top_n_scored = sorted(scored_sentences, key=lambda s: s[1])[-TOP_SENTENCES:]
    top_n_scored = sorted(top_n_scored, key=lambda s: s[0])
    top_n_summary=[sentences[idx] for (idx, score) in top_n_scored]
    return ', '.join(top_n_words[:18]), u'。 '.join(top_n_summary) + u'。', cls

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

    (top_n_words,_) = key_words(txt, N_3)
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
def sim_search(html):
    model_pks = []
    scores = []
    results = None
    try:
        results = server.find_similar('html_%d' % html.id)
        #print 'get from id',html.id,results
    except:
        doc = {}
        doc['tokens'] = [s for s in Tokenize(html.content)]
        results = server.find_similar(doc)
        #print 'get from content'
    if results:
        for result in results:
            id = int(result[0].split('_')[1])
            model_pks.append(id)
            scores.append(result[1])
        objs = []
        bulk_objs = HtmlContent.objects.in_bulk(model_pks)
        for k,v in enumerate(model_pks):
            objs.append((bulk_objs[v],scores[k]))
        return objs
        #return list(HtmlContent.objects.filter(pk__in=model_pks))
    else:
        return None

def sim_content(content):
    model_pks = []
    scores = []
    doc = {}
    '''
    if not isinstance(content,unicode):
        try:
            content = content.decode('utf-8')
        except:
            content = content.decode('gbk','ignore').encode('utf-8', 'replace').decode('utf-8')
    '''
    doc['tokens'] = [s for s in Tokenize(content)]
    #print doc
    results = server.find_similar(doc)
    if results:
        for result in results:
            id = int(result[0].split('_')[1])
            model_pks.append(id)
            scores.append(result[1])
        objs = []
        bulk_objs = HtmlContent.objects.in_bulk(model_pks)
        for k,v in enumerate(model_pks):
            objs.append((bulk_objs[v],scores[k]))
        return objs
    else:
        return None

def sim_index(obj):
    doc = {}
    doc['id'] = 'html_%d' % obj.id
    doc['tokens'] = [s for s in Tokenize(obj.content)]
    server.index([doc])

