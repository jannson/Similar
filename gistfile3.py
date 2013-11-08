import sys, os, os.path
import logging
import pprint
import gensim
from gensim import models, corpora, similarities
from collections import defaultdict
import json
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster, ward
from sklearn.cluster.affinity_propagation_ import affinity_propagation
from sklearn.cluster import KMeans, AffinityPropagation
from sklearn.cluster import KMeans
import numpy as np
import codecs
import heapq

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(levelname)s:%(name)s:%(threadName)s: %(message)s")
logger = logging.getLogger(__name__)

GENSIM_DATA_ROOT = "/home/gan/project/source/testgit/Similar"
LSI_MODEL_FILE = os.path.join(GENSIM_DATA_ROOT, "wiki_en_model.lsi")
TFIDF_MODEL_FILE = os.path.join(GENSIM_DATA_ROOT, "wiki_en_tfidf.model")
CORPUS_FILE = os.path.join(GENSIM_DATA_ROOT, "wiki_en_corpus.mm")
DICTIONARY_FILE = os.path.join(GENSIM_DATA_ROOT, "wiki_en_wordids.txt")
SHARD_DIR = os.path.join('/tmp', "index_shards")

def load_gensim_tools():
    """Load serialized objects."""

    dictionary = corpora.Dictionary.load_from_text(DICTIONARY_FILE)

    # TODO chain transformations
    tfidf_transformation = models.tfidfmodel.TfidfModel.load(TFIDF_MODEL_FILE)

    lsi_transformation = models.lsimodel.LsiModel.load(LSI_MODEL_FILE)

    return dictionary, tfidf_transformation, lsi_transformation

def create_index(corpus):
    """Create an index given a corpus and transformation(s).
        :param corpus: The index corpus (documents against which new unseen documents will be compared)
        :param tfidf_transformation: A vector space transformation model
        :param lsi_transformation: A vector space transformation model
        """
    # Ensure a dir exists to store the shards
    index_dir = SHARD_DIR
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)

    # Create the index
    index = similarities.Similarity(index_dir + "/shard",
        corpus=corpus,
        num_features=400,  # TODO don't hard code this
    )

    return index

def print_sims(query):
    sims = index[query]
    
    result = []
    for i in np.argsort(sims)[::-1]:
        if abs(sims[i]) > 1e-10:
            result.append((i,sims[i]))
            if len(result) == 10:
                break

    #result = heapq.nlargest(10, sims)
    #print result

    #fmt = ["%s(%f)" % (dictionary[idother], sim) for idother,sim in enumerate(sims)]
    fmt = ["%s(%f)" % (dictionary[idother], sim) for idother,sim in result]
    print "the query is similar to ", ','.join(fmt)

def print_group(index_term):
    with codecs.open('zzz2','w','utf-8') as file:
        for sims in index_term:
            result = []
            for i in np.argsort(sims)[::-1]:
                if abs(sims[i]) > 1e-10:
                    result.append((i,sims[i]))
                    if len(result) == 10:
                        break
            fmt = ["%s(%f)" % (dictionary[idother], sim) for idother,sim in result]
            str_term = ','.join(fmt) + '\n'
            file.write(str_term.decode('utf-8'))

if __name__ == "__main__":
    dictionary, tfidf_transformation, lsi_transformation = load_gensim_tools()

    term_corpus = gensim.matutils.Dense2Corpus(lsi_transformation.projection.u.T)
    index = create_index(term_corpus)

    #Search the similiar words
    #query = list(term_corpus)[0]
    #print_sims(query)
   
    print 'begin index'
    index_term = index[term_corpus]
    #sims = [s for s in index_term]
    print 'output group'
    print_group(index_term)
    
    #print 'begin affinity'
    #cluster_centers_indices, labels = affinity_propagation(sims)

    #af = AffinityPropagation(affinity="euclidean").fit(lsi_transformation.projection.u)
    #luster_centers_indices = af.cluster_centers_indices_
    #labels = af.labels_
    #print labels.shape

    #k = KMeans(init='k-means++', n_init=10)
    #k.fit(lsi_transformation.projection.u)
    #centroids = k.cluster_centers_
    #labels = k.labels_
    
    #print 'begin output'
    #doc_arr = np.array(range())
    #for i in range(np.max(labels)):
    #    print 'group:', (i+1)
    #    for doc_num in doc_arr[labels==i]:
    #        print dictionary[doc_num] + '/',
    #    print '\n'

    
