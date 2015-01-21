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
print idx[::-1]
print a[:,idx]
print '\n'

a = np.array([[1,2,3],[4,5,6]])
b = np.array([[7,8],[9,10],[11,12]])
#print np.dot(a, b)
#print np.outer(a,b)
#print np.mean(a)
#print a.mean(axis=0)
print b[[1,1,0]]

ar = np.array([[1,2,3],[4,5,6],[7,8,9],[10,11,12]])
print '\nar', ar[:,-1:]
print 'repeat', np.repeat(ar[:, -1:], 5, axis=1)
print 'some cols', ar[:, 1:2]

print 'random test', np.random.random([5,3])

ar = np.array([9, 4, 4, 3, 3, 9, 0, 4, 6, 0])
ind = np.argpartition(ar, -2)[:ar.shape[0]-2]
print ind
print ar[ind]
#print list(set(range(ar.shape[0])) - set([n for n in ind]))
#print np.argpartition(ar, -4)[:ar.shape[0]-4]
#print ar[ind]
#print ind[np.argsort(ar[ind])]
#print ar
#print ar[ind]
#ar[ind] = np.zeros(ind.shape[0])
#print ar

#ar = ar.reshape([ar.shape[0]/2, 2])
#print ar
#ind = np.argpartition(ar, -2, axis=1)
#print ind

#print ar.reshape(ar.shape[0]*ar.shape[1])
