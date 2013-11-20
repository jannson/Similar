import logging
from gensim import corpora, models, similarities, matutils

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

dictionary = corpora.Dictionary.load('/tmp/deerwester.dict')
corpus = corpora.MmCorpus('/tmp/deerwester.mm')
print list(corpus)
#print matutils.corpus2dense(corpus, 28)
print '\n'
#print matutils.dense2vec(matutils.corpus2dense(corpus, 28))
#print matutils.corpus2csc(corpus)
print '\n'

tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
doc_bow = [(0, 1), (1, 1)]
print tfidf[doc_bow] # step 2 -- use the model to transform vectors
print '\n'

corpus_tfidf = tfidf[corpus]
for doc in corpus_tfidf:
    print doc
print '\n'
print matutils.corpus2csc(corpus_tfidf)

lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=2) # initialize an LSI transformation
corpus_lsi = lsi[corpus_tfidf] # create a double wrapper over the original corpus: bow->tfidf->fold-in-lsi
print matutils.corpus2csc(corpus_lsi)
#print matutils.Sparse2Corpus(matutils.corpus2csc(corpus_lsi))
#lsi.print_topics(2)
print '\n'

for doc in corpus_lsi: # both bow->tfidf and tfidf->lsi transformations are actually executed here, on the fly
    print doc
print '\n'

lsi.save('/tmp/model.lsi') # same for tfidf, lda, ...
lsi = models.LsiModel.load('/tmp/model.lsi')

