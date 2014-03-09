# Copyright 2006 Bryan O'Sullivan <bos@serpentine.com>.
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, version 2 or later, which is
# incorporated herein by reference.

class SlopeOne(object):
    def __init__(self):
        self.diffs = {}
        self.freqs = {}

    def predict(self, userprefs):
        preds, freqs = {}, {}
        for item, rating in userprefs.iteritems():
            for diffitem, diffratings in self.diffs.iteritems():
                try:
                    freq = self.freqs[diffitem][item]
                except KeyError:
                    continue
                preds.setdefault(diffitem, 0.0)
                freqs.setdefault(diffitem, 0)
                preds[diffitem] += freq * (diffratings[item] + rating)
                freqs[diffitem] += freq
        return dict([(item, value / freqs[item])
                     for item, value in preds.iteritems()
                     if item not in userprefs and freqs[item] > 0])

    def update(self, userdata):
        for ratings in userdata.itervalues():
            for item1, rating1 in ratings.iteritems():
                self.freqs.setdefault(item1, {})
                self.diffs.setdefault(item1, {})
                for item2, rating2 in ratings.iteritems():
                    self.freqs[item1].setdefault(item2, 0)
                    self.diffs[item1].setdefault(item2, 0.0)
                    self.freqs[item1][item2] += 1
                    self.diffs[item1][item2] += rating1 - rating2
        for item1, ratings in self.diffs.iteritems():
            for item2 in ratings:
                print item1, item2, ratings[item2]
                ratings[item2] /= self.freqs[item1][item2]

if __name__ == '__main__':
    userdata = dict(
        a=dict(s1=1.0,
                   s2=3.0,
                   s3=1.0),
        b=dict(s1=3.0,
                   s2=3.0,
                   s3=3.0),
        d=dict(s1=3.0,
                   s2=1.0),
        )
    s = SlopeOne()
    s.update(userdata)
    print s.predict(dict(s1=3.0,
                   s3=1.0))
