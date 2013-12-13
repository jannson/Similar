# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from cppjiebapy import Tokenize, cut_sentence
import textrank

def key_rank(text, topk=18):
    sents = list(cut_sentence(text))
    docs = [list(Tokenize(sent)) for sent in sents]
    keyword_rank = textrank.KeywordTextRank(docs)
    keyword_rank.solve()
    keys = [w for w in keyword_rank.top_index(topk)]
    return keys

def sum_rank(text):
    sents = list(cut_sentence(obj.content))
    docs = [list(Tokenize(sent)) for sent in sents]
    sim_res = bm25_weights(docs)
    rank = TextRank(sim_res)
    rank.solve()
    top_n_summary = []
    for index in sorted(rank.top_index(3)):
        top_n_summary.append(sents[index])
    return u'。 '.join(top_n_summary).replace('\r','').replace('\n','')+u'。'
