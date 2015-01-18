import numpy as np


a = np.array([1, 1, 1, 1])
b = np.array([1, 1, -1, -1])
print np.dot(a, b)

c = (a**2 * b.T**2)
print np.sqrt(np.sum(c))
