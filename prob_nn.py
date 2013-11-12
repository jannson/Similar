import math

data = {'o' : [(0.2, 0.5), (0.5, 0.7)],
        'x' : [(0.8, 0.8), (0.4, 0.5)],
        'i' : [(0.8, 0.5), (0.6, 0.3), (0.3, 0.2)]}

class Prob_Neural_Network(object):
    def __init__(self, data):
        self.data = data

    def predict(self, new_point, sigma):
        res_dict = {}
        np = new_point
        for k, v in self.data.iteritems():
            res_dict[k] = sum(self.gaussian_func(np[0], np[1], p[0], p[1], sigma) for p in v)
        return max(res_dict.iteritems(), key=lambda k : k[1])

    def gaussian_func(self, x, y, x_0, y_0, sigma):
        return  math.e ** (-1 *((x - x_0) ** 2 + (y - y_0) ** 2) / ((2 * (sigma ** 2))))

prob_nn = Prob_Neural_Network(data)
res = prob_nn.predict((0.2, 0.6), 0.1)
print res
