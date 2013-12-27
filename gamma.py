import numpy as np
import matplotlib.pyplot as plt
import scipy.special as sps

shape, scale = 100., 1./100.
s = np.random.gamma(shape, scale, 1000)

count, bins, ignored = plt.hist(s, 50, normed=True)
y = bins**(shape-1)*(np.exp(-bins/scale)/(sps.gamma(shape)*scale**shape))
plt.plot(bins,y,linewidth=2,color='r')
plt.show()
