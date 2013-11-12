import os
import logging
import gensim
from gensim.models import Word2Vec

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

document = open('sentence.txt','r')
sentences = [list(gensim.utils.tokenize(line, lower=True)) for line in document]
model = Word2Vec(sentences, size=100, window=5, min_count=5, workers=4)

print model.most_similar(positive=['we'], negative=['you'])
