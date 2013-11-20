# -*- coding: utf-8 -*-
import os, codecs, re, sys
import numpy as np
import itertools
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from cppjiebapy import Tokenize

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
