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

def input_test():
    all_objs = []
    with codecs.open('trainsmall.txt', 'r', 'utf-8') as f:
        for line in f:
            items = line.split()
            if len(items) > 2:
                xh = XhLogUd()
                xh.guid = items[0]
                xh.post_id = int(items[1])
                score = int(items[2])
                if score == 1:
                    xh.uaction = 'd'
                else:
                    xh.uaction = 'u'
                xh.pos = 'z'
                xh.shiduan = 9
                xh.ctime = 9
                #xh.save()
                all_objs.append(xh)
    return all_objs

#input_test()

def rank2():
    #all_objs = input_test()
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
    good_post = 1
    bad_post = 1
    for obj in all_objs:
        if obj.uaction == 'u':
            posts1[post2id[obj.post_id]].add(guid2id[obj.guid])
            good_post += 1
        else:
            posts2[post2id[obj.post_id]].add(guid2id[obj.guid])
            bad_post += 1
    good_bad = math.sqrt(float(good_post)/float(bad_post))

    print "all users", len(id2guid)
    print "all items", len(id2post)
    
    scores = []
    for x in xrange(len(id2post)):
        score1 = 1
        if len(posts1[x]) > 0:
            for y in posts1[x]:
                len_y = len(guids1[y])
                if y > 1:
                    score1 += (len_y**2)/good_bad
            score1 *= math.sqrt(len(posts1[x])+1)

        score2 = 1
        if len(posts2[x]) > 0:
            for y in posts2[x]:
                len_y = len(guids2[y])
                if y > 1:
                    score2 += (len_y**2)*good_bad
            score2 *= math.sqrt(len(posts2[x])+1)
        scores.append(score1/score2)

    res = sorted( [(scores[i],id2post[i]) for i in xrange(len(id2post))] , reverse=True)
    #print res[0][0]/res[1][0]

    with open('rank2.out', 'w') as f:
        for r in res:
            f.write('%d %f\n' % (r[1], r[0]) )

rank2()

