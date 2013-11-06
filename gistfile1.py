import sys, os, os.path
import logging
from scipy.odr import models
import unittest
import os
import os.path
import tempfile

import numpy
import gensim
import logging

from gensim.corpora import mmcorpus, Dictionary
from gensim.models import lsimodel, ldamodel, tfidfmodel, rpmodel, logentropy_model, TfidfModel, LsiModel
from gensim import matutils,corpora

django_path = '/home/gan/project/source/svn_project/pull/1'
sys.path.insert(13, django_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'pull.settings'

from django.db.models import Count
from django.db.models import Q
from pull.models import *

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def iter_documents():
    """Iterate over all documents, yielding a document (=list of utf8 tokens) at a time."""
    for obj in HtmlContent.objects.filter(~Q(retry=3)).filter(~Q(content='')):
        document = obj.content
        yield gensim.utils.tokenize(document, lower=True) # or whatever tokenization suits you

class MyCorpus(object):
    def __init__(self):
        self.dictionary = gensim.corpora.Dictionary(iter_documents())
        self.dictionary.filter_extremes(no_below=1, keep_n=30000) # check API docs for pruning params
        self.dictionary.save_as_text('wiki_en_wordids.txt')

    def __iter__(self):
        for tokens in iter_documents():
            yield self.dictionary.doc2bow(tokens)

corpus = MyCorpus() # create a dictionary
corpora.MmCorpus.serialize('wiki_en_corpus.mm', corpus) # store to disk, for later use

#for vector in corpus: # convert each document to a bag-of-word vector
#    print vector

print "Create models"
tfidf_model = TfidfModel(corpus)
tfidf_model.save('wiki_en_tfidf.model')

#lsi_model = LsiModel(corpus)

#topic_id = 0
#for topic in lsi_model.show_topics():
#    topic_id+=1
#    print "TOPIC (LSI) " + str(topic_id) + " : " + topic

#lsi_model.print_topic(20, topn=10)
#corpus_lsi = lsi_model[corpus]

corpus_tfidf = tfidf_model[corpus]

lsi_model_2 = LsiModel(corpus_tfidf, id2word=corpus.dictionary, num_topics=300)
corpus_lsi_2 = lsi_model_2[corpus]
print "Done creating models"

lsi_model_2.save('wiki_en_model.lsi')

#lsi_model_2 .print_topics(5)

'''
topic_id = 0
for topic in lsi_model_2.show_topics():
    print "TOPIC (LSI2) " + str(topic_id) + " : " + topic
    #group_topic = [doc for doc in corpus_lsi_2 if doc[topic_id] > 0.5]
    group_topic = [doc for doc in corpus_lsi_2]
    print str(group_topic)
    topic_id+=1
'''





print "Docs Processed " + str(lsi_model_2.docs_processed)

#for doc in corpus_lsi_2: # both bow->tfidf and tfidf->lsi transformations are actually executed here, on the fly
#    print "Doc " + str(doc)

#
#
#corpus.dictionary.save("dictionary.dump")
#
#tfidf_model.save("model_tfidf.dump")
#corpus_tfidf.save("corpus_tfidf.dump")
#
#lsi_model.save("model_lsi.dump")
#corpus_lsi.save("corpus_lsidump")
#
#
#lsi_model_2.save("model_lsi_2.dump")
#corpus_lsi_2.save("corpus_lsi_2.dump")

#for doc in corpus_tfidf:
#    print doc
