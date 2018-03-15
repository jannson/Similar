# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from cppjiebapy import  Tokenize, cut_sentence
from extractor import Extractor
import textrank
from bm25 import bm25_weights

def tokenize2(text):
    for k in Tokenize(text):
        if len(k) > 1:
            yield k

def key_rank(text, topk=18):
    sents = list(cut_sentence(text))
    docs = [list(tokenize2(sent)) for sent in sents]
    keyword_rank = textrank.KeywordTextRank(docs)
    keyword_rank.solve()
    keys = [w for w in keyword_rank.top_index(topk)]
    return keys

def sum_rank(text):
    sents = list(cut_sentence(text))
    docs = [list(tokenize2(sent)) for sent in sents]
    sim_res = bm25_weights(docs)
    rank = textrank.TextRank(sim_res)
    rank.solve()
    top_n_summary = []
    for index in sorted(rank.top_index(3)):
        top_n_summary.append(sents[index])
    return u'。 '.join(top_n_summary).replace('\r','').replace('\n','')+u'。'

if __name__ == '__main__':
    ext = Extractor(url="http://news.cctv.com/2018/03/14/ARTIae5nIxMetJzk20Gk8Vw7180314.shtml",blockSize=5, image=False)
    content = ext.getContext()
    print(repr(key_rank(content)).decode('unicode-escape'))
