import sys, os, os.path
import logging
import pprint
import gensim
from gensim import models, corpora, similarities
from collections import defaultdict
import json
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster, ward
from sklearn.cluster.affinity_propagation_ import affinity_propagation
import numpy as np
import codecs

django_path = '/home/gan/project/source/svn_project/pull/1'
sys.path.insert(13, django_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'pull.settings'

from django.db.models import Count
from django.db.models import Q
from pull.models import HtmlContent

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

def create_corpus():
    #return [word2id.doc2bow(gensim.utils.tokenize(text, lower=True)) for text in docs]
    return corpora.MmCorpus(CORPUS_FILE)

def create_index(corpus, tfidf_transformation, lsi_transformation):
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
        corpus=lsi_transformation[tfidf_transformation[corpus]],
        num_features=400,  # TODO don't hard code this
    )

    return index

if __name__ == "__main__":
    dictionary, tfidf_transformation, lsi_transformation = load_gensim_tools()
    corpus = create_corpus()
    index = create_index(corpus, tfidf_transformation, lsi_transformation)

    tfidf_vec_doc = tfidf_transformation[corpus]
    lsi_vec_doc = lsi_transformation[tfidf_vec_doc]
    #lsi_transformation.print_topics(10)
    
    index_doc = index[lsi_vec_doc]
    sims = [s for s in index_doc]

    cluster_centers_indices, labels = affinity_propagation(sims)
   
    docs = []
    for obj in HtmlContent.objects.filter(~Q(retry=3)).filter(~Q(content='')):
        docs.append(obj.title)

    doc_arr = np.array(range(len(labels)))

    with codecs.open('zzz','w','utf-8') as file:
        for i in range(np.max(labels)):
            output = 'group:'+str(i+1)+'\n'
            for doc_num in doc_arr[labels==i]:
                output += docs[doc_num] + ' / '
            output += '\n'
            file.write(output)
