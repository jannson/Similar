import sys, os, os.path
import codecs
from scipy.sparse import *
from scipy import *

django_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(13, django_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'xxhh.settings'

from django.db.models import Count
from django.db.models import Q
from xxhh.models import *

diff = lil_matrix( (100000,100000), dtype=float)
diff[1,2] = 8.0
diff[0,1] = 2.0

for a in diff.nonzero():
    print a[0], a[1]

#for obj in XhLogUd.objects.all()[0:10]:
#    print obj.post_id, obj.guid, obj.uaction

#for obj in XhLogUd.objects.filter(post_id=67400):
#    print obj.post_id, obj.guid, obj.uaction

#for obj in XhLogUd.objects.filter(guid='11a2458d-6a38-ccde-e176-af0971b26daf'):
#    print obj.post_id, obj.guid, obj.uaction

#print len(XhLogUd.objects.values("guid").distinct())
#print len(XhLogUd.objects.values("post_id").distinct())

RATE = {}
RATE['u'] = 1.0
RATE['d'] = (0.0-1.0)

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

#ratings = Ratings()
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

        for pair in self.freq_like.nonzero():
            if len(pair) == 0:
                break
            if pair[0] < pair[1] and self.freq_dislike[pair[0], pair[1]] != 0:
                self.diff_like[pair[0], pair[1]] /= self.freq_like[pair[0], pair[1]]
        for pair in self.freq_dislike.nonzero():
            if len(pair) == 0:
                break
            if pair[0] < pair[1] and self.freq_dislike[pair[0], pair[1]] != 0:
                self.diff_dislike[pair[0], pair[1]] /= self.freq_dislike[pair[0], pair[1]]

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
                    prediction += self.diff_like[item_id, rate[2]] + rate[0]
                    freqs += f
            else:
                f = self.freq_dislike[item_id, rate[2]]
                if f != 0:
                    prediction += self.diff_dislike[item_id, rate[2]] + rate[0]
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
            print 'Begin train for user %s len=%d' % (user_id, len(self.ratings.by_user(user_id)))
            for rate1 in self.ratings.by_user(user_id):
                for rate2 in self.ratings.by_user(user_id):
                    self.freq_like[rate1[2], rate2[2]] += 1
                    self.diff_like[rate1[2], rate2[2]] += rate1[0]-rate2[0]

        for pair in self.freq_like.nonzero():
            if len(pair) == 0:
                break
            if pair[0] < pair[1]:
                self.diff_like[pair[0], pair[1]] /= self.freq_like[pair[0], pair[1]]

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
                prediction += self.diff_like[item_id, rate[2]] + rate[0]
                freqs += f
        if freqs == 0:
            return 0
        return prediction / freqs

slope = WeightSlopeOne(ratings)
'''
slope.train()
print 'train complete'
print ratings.id2guid[2], ratings.id2post[2],  slope.perdict(2, 3)
'''
