import sys, os, os.path, re
import codecs
import numpy as np
from scipy.sparse import *
from scipy import *
from sklearn.externals import joblib
import networkx as nx

django_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(13, django_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'xxhh.settings'

from django.db.models import Count
from django.db.models import Q
#from xxhh.models import TestLog as XhLogUd
from xxhh.models import XhLogUd

RATE = {}
RATE['u'] = 1
RATE['d'] = -1

class Ratings(object):
    def __init__(self):
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

        self.guid2id = guid2id
        self.id2guid = id2guid
        
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

        self.post2id = post2id
        self.id2post = id2post

        guids = [[] for _ in id2guid]
        for obj in all_objs:
            guids[guid2id[obj.guid]].append((RATE[obj.uaction.strip()], self.guid2id[obj.guid], self.post2id[obj.post_id]))
        self.guids = guids

        posts1 = [set() for _ in id2post]
        posts2 = [set() for _ in id2post]
        for obj in all_objs:
            if obj.uaction == 'u':
                posts1[post2id[obj.post_id]].add(guid2id[obj.guid])
            else:
                posts2[post2id[obj.post_id]].add(guid2id[obj.guid])
        '''
        post_max = 0
        for guid_set in self.posts:
            if post_max < len(guid_set):
                post_max = len(guid_set)
        print "max guids in post", post_max
        '''

        print "all users", len(self.id2guid)
        print "all items", len(self.id2post)
        
        #sorting users
        #sorted_guids = [(g,len(self.guids[self.guid2id[g]]) ) for i,g in enumerate(self.id2guid)]
        #self.sorted_guids = [g for g,c in sorted(sorted_guids, key = lambda item: -item[1]) if c >= 3]
        #print self.sorted_guids[0:10]
        #print 'len and max rated guid', len(self.sorted_guids), self.sorted_guids[0], len(self.guids[self.guid2id[self.sorted_guids[0]]])

        weights1 = np.zeros((len(id2post),len(id2post)), dtype=float)
        weights2 = np.zeros((len(id2post),len(id2post)), dtype=float)
        #weights =  lil_matrix( (len(id2post), len(id2post)), dtype=float)
        for x in xrange(len(id2post)):
            for y in xrange(len(id2post)):
                if x < y:
                    weights1[x,y] = len(posts1[x] & posts1[y])
                    weights2[x,y] = len(posts2[x] & posts2[y])
                else:
                    weights1[x,y] = weights1[y,x]
                    weights2[x,y] = weights2[y,x]

        weights1 = weights1/len(self.id2post)
        weights2 = weights2/len(self.id2post)

        nx_graph = nx.from_numpy_matrix(weights1)
        scores1 = nx.pagerank_numpy(nx_graph)
        print 'score1 complete'

        nx_graph = nx.from_numpy_matrix(weights2)
        scores2 = nx.pagerank_numpy(nx_graph)
        print 'score1 complete'

        scores = [scores1[i]/scores2[i] for i in xrange(len(id2post))]
        #nx_graph = nx.from_scipy_sparse_matrix(self.weights)
        #scores = nx.pagerank_scipy(nx_graph)
        res = sorted( [(scores[i],id2post[i]) for i in xrange(len(id2post))] , reverse=True)

        with open('rank.out', 'w') as f:
            for r in res:
                f.write('%d %f\n' % (r[1], r[0]) )
    

    def by_user(self, id):
        return self.guids[id]

    def all_users(self):
        for guid in self.sorted_guids:
            yield self.guid2id[guid]

ratings = Ratings()
