import numpy as np
import itertools
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

measurements = [
        {'city':'Dubai', 'temperature':33.},
        {'city':'London', 'temperature':12.},
        {'city':'San Fransisco', 'temperature': 18.},
        ]
vec = DictVectorizer()
print vec.fit_transform(measurements).toarray()
print vec.get_feature_names()
print '\n'

vectorizer = CountVectorizer(min_df=1)
corpus = [
        ' This is the first document.',
        'This is the seconds document.',
        'And the third one.',
        'Is this the first document?',]
X = vectorizer.fit_transform(corpus)
print vectorizer.get_feature_names()
print X
print X.toarray()
analyzer = vectorizer.build_analyzer()
print analyzer("This is a text document to analyzer.")
print '\n'

transformer = TfidfTransformer()
counts = [[3, 0, 1],
           [2, 0, 0],
           [3, 0, 0],
           [4, 0, 0],
           [3, 2, 0],
           [3, 0, 2]]

tfidf = transformer.fit_transform(counts)
print tfidf.toarray()
print '\n'

vectorizer = TfidfVectorizer(min_df=1)
X = vectorizer.fit_transform(corpus)
print X
print '\n'
