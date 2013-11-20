import numpy as np
import itertools
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from cppjiebapy import Tokenize

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

tags = [
  "python, tools",
  "linux, tools, ubuntu",
  "distributed systems, linux, networking, tools",
]

print list(Tokenize(tags[-1]))

vec = CountVectorizer(tokenizer=Tokenize)
data = vec.fit_transform(tags)
print data

vocab = vec.get_feature_names()
print vocab

print "#####HASHING TESTING#########"
vec = HashingVectorizer(tokenizer=Tokenize)
data = vec.fit_transform(tags)
print data
print "###END HASHING###"

train_set = ["The sky is blue.", "The sun is bright."] #Documents
test_set = ["The sun in the sky is bright."] #Query

vectorizer = CountVectorizer(tokenizer=Tokenize)
transformer = TfidfTransformer()

trainVectorizerArray = vectorizer.fit_transform(train_set).toarray()
testVectorizerArray = vectorizer.transform(test_set).toarray()
print 'Fit Vectorizer to train set\n', trainVectorizerArray
print 'Transform Vectorizer to test set\n', testVectorizerArray

transformer.fit(trainVectorizerArray)
print transformer.transform(trainVectorizerArray).toarray()

transformer.fit(testVectorizerArray)

tfidf = transformer.transform(testVectorizerArray)
print tfidf.todense()

X = [[0., 0.], [1., 1.]]
y = [0, 1]
clf = SGDClassifier(loss="hinge", penalty="l2")
clf.fit(X, y)
print clf.predict([[2.,2.]])
