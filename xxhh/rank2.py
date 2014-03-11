import sys, os, os.path, re
import codecs
import numpy as np
from scipy.sparse import *
from scipy import *
from sklearn.externals import joblib
import networkx as nx
import math

django_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(13, django_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'xxhh.settings'

from django.db.models import Count
from django.db.models import Q
#from xxhh.models import TestLog as XhLogUd
from xxhh.models import XhLogUd

def rank2():
    all_objs = list(XhLogUd.objects.exclude(guid=''))
    guid2id = {}
    id2guid = []
    i = 0
    for obj in all_objs:
        if obj.guid not in guid2id:
            guid = obj.guid
            guid2id[guid] = i
            id2guid.append(guid)
            i += 1

    max_item = 0
    post2id = {}
    id2post = []
    i = 0
    for obj in all_objs:
        if obj.post_id not in post2id:
            post_id = obj.post_id
            post2id[post_id] = i
            id2post.append(post_id)
            i += 1

    guids1 = [set() for _ in id2guid]
    guids2 = [set() for _ in id2guid]
    for obj in all_objs:
        if obj.uaction == 'u':
            guids1[guid2id[obj.guid]].add(obj.post_id)
        else:
            guids2[guid2id[obj.guid]].add(obj.post_id)

    posts1 = [set() for _ in id2post]
    posts2 = [set() for _ in id2post]
    for obj in all_objs:
        if obj.uaction == 'u':
            posts1[post2id[obj.post_id]].add(guid2id[obj.guid])
        else:
            posts2[post2id[obj.post_id]].add(guid2id[obj.guid])

    print "all users", len(id2guid)
    print "all items", len(id2post)
    
    scores = []
    for x in xrange(len(id2post)):
        score1 = 0.1
        if len(posts1[x]) > 0:
            for y in posts1[x]:
                len_y = len(guids1[y])
                if y > 2:
                    score1 += math.sqrt(1.0/len_y)
            score1 *= len(posts1[x])

        score2 = 0.1
        if len(posts2[x]) > 0:
            for y in posts2[x]:
                len_y = len(guids2[y])
                if y > 2:
                    score1 += math.sqrt(1.0/len_y)
            score2 *= len(posts2[x])
        scores.append(score1/score2)

    res = sorted( [(scores[i],id2post[i]) for i in xrange(len(id2post))] , reverse=True)

    with open('rank2.out', 'w') as f:
        for r in res:
            f.write('%d %f\n' % (r[1], r[0]) )

rank2()

