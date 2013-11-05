import numpy as np

words = np.array(
    ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
     'I', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
     'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we',
     'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all',
     'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if',
     'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make',
     'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
     'people', 'into', 'year', 'your', 'good', 'some', 'could',
     'them', 'see', 'other', 'than', 'then', 'now', 'look',
     'only', 'come', 'its', 'over', 'think', 'also', 'back',
     'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well',
     'way', 'even', 'new', 'want', 'because', 'any', 'these',
     'give', 'day', 'most', 'us'])

print 'ndim', words.ndim
#(dim,) = words.shape
print 'shape', words.shape
print 'size', words.size
print 'dtype', words.dtype
print 'itemsize', words.itemsize
print 'data', words.data

a = np.arange(15)
print 'arange', a
ar = a.reshape(3,5)
print 'reshape', ar

ar = np.zeros( (7,8) )
ar[3][5] = 0.7
print 'zeros',ar

words = np.array(['aaa','bbb','ccc','ddd'])
ar = np.array([1,2,3,4])
print words[ar==1]

a = np.array([[4,9,2],[5,1,3]])
idx = np.argsort(a[1])
print idx
print a[:,idx]
