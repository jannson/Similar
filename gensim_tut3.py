import logging
from gensim import corpora, models, similarities

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

dictionary = corpora.Dictionary.load('/tmp/deerwester.dict')
corpus = corpora.MmCorpus('/tmp/deerwester.mm') # comes from the first tutorial, "From strings to vectors"
print corpus
print '\n'

lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=2)
doc = "Human computer interaction"
vec_bow = dictionary.doc2bow(doc.lower().split())
vec_lsi = lsi[vec_bow] # convert the query to LSI space
print vec_lsi
print '\n'

index = similarities.MatrixSimilarity(lsi[corpus]) # transform corpus to LSI space and index it
index.save('/tmp/deerwester.index')
index = similarities.MatrixSimilarity.load('/tmp/deerwester.index')
sims = index[vec_lsi] # perform a similarity query against the corpus
print list(enumerate(sims)) # print (document_number, document_similarity) 2-tuples
print '\n'

sims = sorted(enumerate(sims), key=lambda item: -item[1])
print sims # print sorted (document number, similarity score) 2-tuples
print '\n'

