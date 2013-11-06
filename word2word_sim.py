import logging
from gensim import corpora, models, similarities
import gensim

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

dictionary = corpora.Dictionary.load('/tmp/deerwester.dict')
corpus = corpora.MmCorpus('/tmp/deerwester.mm')
print list(corpus)
print '\n'

tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
doc_bow = [(0, 1), (1, 1)]
print tfidf[doc_bow] # step 2 -- use the model to transform vectors
print '\n'

corpus_tfidf = tfidf[corpus]
for doc in corpus_tfidf:
    print doc
print '\n'

lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=2) # initialize an LSI transformation
#term_corpus = gensim.matutils.Dense2Corpus((lsi.projection.u*lsi.projection.s).T)
term_corpus = gensim.matutils.Dense2Corpus(lsi.projection.u.T)
print 'lsi.projection.u.T'
print lsi.projection.u.T
print '\n'
print 'lsi.projection.u*s'
print lsi.projection.u
#print (lsi.projection.u*lsi.projection.s)
print '\n'
print list(term_corpus)
print '\n'

index = gensim.similarities.MatrixSimilarity(term_corpus)

def print_sims(query):
    sims = index[query]
    fmt = ["%s(%f)" % (dictionary[idother], sim) for idother,sim in enumerate(sims)]
    print "the query is similar to ", ','.join(fmt)

query = list(term_corpus)[0]
print_sims(query)

