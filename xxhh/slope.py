import sys, os, os.path
import codecs
from scipy.sparse import *
from scipy import *
from sklearn.externals import joblib

django_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(13, django_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'xxhh.settings'

from django.db.models import Count
from django.db.models import Q
from xxhh.models import TestLog as XhLogUd
#from xxhh.models import XhLogUd

diff = lil_matrix( (100000,100000), dtype=float)
diff[1,2] = 8.0
diff[0,1] = 2.0
diff[4,5] = 1.0

#for a in diff.nonzero():
#    print a

def input_test():
    with codecs.open('trainsmall.txt', 'r', 'utf-8') as f:
        for line in f:
            items = line.split()
            print items
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
                xh.save()
#input_test()

#for obj in XhLogUd.objects.all()[0:10]:
#    print obj.post_id, obj.guid, obj.uaction

#for obj in XhLogUd.objects.filter(post_id=67400):
#    print obj.post_id, obj.guid, obj.uaction

#for obj in XhLogUd.objects.filter(guid='11a2458d-6a38-ccde-e176-af0971b26daf'):
#    print obj.post_id, obj.guid, obj.uaction

#print len(XhLogUd.objects.values("guid").distinct())
#print len(XhLogUd.objects.values("post_id").distinct())

RATE = {}
RATE['u'] = 3.0
RATE['d'] = 1.0

class Ratings(object):
    def __init__(self):
        all_objs = list(XhLogUd.objects.all())
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

    def by_user(self, id):
        return self.guids[id]

ratings = Ratings()
print 'Ratings created'

'''
for user_id in range(len(ratings.id2guid)):
    for rate in ratings.by_user(user_id):
        print "%d %d %d" % (rate[1], rate[2], int(rate[0]))
    print ""
'''

class BiPolarSlopeOne(object):
    def __init__(self, ratings):
        self.ratings = ratings

    def init_model(self):
        self.diff_like = lil_matrix((10000,10000), dtype=float)
        self.freq_like = lil_matrix((10000,10000), dtype=int)
        self.diff_dislike = lil_matrix((10000,10000), dtype=float)
        self.freq_dislike = lil_matrix((10000,10000), dtype=float)
        self.user_average = [0 for _ in self.ratings.id2guid]

    def train(self):
        self.init_model()

        for user_id in xrange(len(self.ratings.id2guid)):
            user_avg = 0.0
            for rate in self.ratings.by_user(user_id):
                user_avg += rate[0]
            user_avg = user_avg/len(self.ratings.by_user(user_id))
            self.user_average[user_id] = user_avg

            for rate1 in self.ratings.by_user(user_id):
                for rate2 in self.ratings.by_user(user_id):
                    if rate1[0] >= user_avg and rate2[0] >= user_avg:
                        self.freq_like[rate1[2], rate2[2]] += 1
                        self.diff_like[rate1[2], rate2[2]] += rate1[0]-rate2[0]
                    elif rate1[0] < user_avg and rate2[0] < user_avg:
                        self.freq_dislike[rate1[2], rate2[2]] += 1
                        self.diff_dislike[rate1[2], rate2[2]] += rate1[0]-rate2[0]

        not_zero = self.freq_like.nonzero()
        if len(not_zero) > 0:
            for index in xrange(len(not_zero[0])):
                x = not_zero[0][index]
                y = not_zero[1][index]
                if x < y:
                    self.diff_like[x, y] /= self.freq_like[x, y]
        not_zero = self.freq_like.nonzero()
        if len(not_zero) > 0:
            for index in xrange(len(not_zero[0])):
                x = not_zero[0][index]
                y = not_zero[1][index]
                if x < y:
                    self.diff_dislike[x, y] /= self.freq_dislike[x, y]

    def can_predict(self, user_id, item_id):
        for rate in self.ratings.by_user(user_id):
            if self.freq_like[item_id, rate[2]] != 0:
                return True
            if self.freq_dislike[item_id, rate[2]] != 0:
                return True
        return False

    def perdict(self, user_id, item_id):
        prediction = 0.0
        freqs = 0

        for rate in self.ratings.by_user(user_id):
            if rate[0] >= self.user_average[user_id]:
                f = self.freq_like[item_id, rate[2]]
                if f != 0:
                    prediction += (self.diff_like[item_id, rate[2]] + rate[0])*f
                    freqs += f
            else:
                f = self.freq_dislike[item_id, rate[2]]
                if f != 0:
                    prediction += (self.diff_dislike[item_id, rate[2]] + rate[0])*f
                    freqs += f
        if freqs == 0:
            return 0
        return prediction / freqs

'''
bi_slope = BiPolarSlopeOne(ratings)
bi_slope.train()
#print bi_slope.perdict(2, 3)
print bi_slope.perdict(0, 2)
'''


class WeightSlopeOne(object):
    def __init__(self, ratings):
        self.ratings = ratings

    def init_model(self):
        post_len = len(self.ratings.id2post)
        self.diff_like = lil_matrix((post_len, post_len), dtype=float)
        self.freq_like = lil_matrix((post_len, post_len), dtype=int)

    def train(self):
        self.init_model()

        for user_id in xrange(len(self.ratings.id2guid)):
            #print 'Begin train for user %s len=%d' % (user_id, len(self.ratings.by_user(user_id)))
            for rate1 in self.ratings.by_user(user_id):
                for rate2 in self.ratings.by_user(user_id):
                    self.freq_like[rate1[2], rate2[2]] += 1
                    self.diff_like[rate1[2], rate2[2]] += rate1[0]-rate2[0]
        
        not_zero = self.freq_like.nonzero()
        if len(not_zero) > 0:
            for index in xrange(len(not_zero[0])):
                x = not_zero[0][index]
                y = not_zero[1][index]
                #if x < y:
                if x != y:
                    self.diff_like[x, y] /= self.freq_like[x, y]

    def can_predict(self, user_id, item_id):
        for rate in self.ratings.by_user(user_id):
            if self.freq_like[item_id, rate[2]] != 0:
                return True
        return False

    def perdict(self, user_id, item_id):
        prediction = 0.0
        freqs = 0

        for rate in self.ratings.by_user(user_id):
            f = self.freq_like[item_id, rate[2]]
            if f != 0:
                prediction += (self.diff_like[item_id, rate[2]] + rate[0])*f
                freqs += f
        if freqs == 0:
            return 0
        return prediction / freqs

    def save(self, filename):
        _ = joblib.dump(self.diff_like, filename+'.diff', compress=9)
        _ = joblib.dump(self.freq_like, filename+'.freq', compress=9)

#slope = BiPolarSlopeOne(ratings)
slope = WeightSlopeOne(ratings)
slope.train()
slope.save('out')
print 'train complete'

#print ratings.guid2id[u'C'], ratings.post2id[2]
#print slope.perdict(ratings.guid2id[u'C'], ratings.post2id[2])
