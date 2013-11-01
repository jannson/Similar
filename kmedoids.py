import numpy as np
import mlpy

class distance:    
    def compute(self, s1, s2):
        l1 = len(s1)
        l2 = len(s2)
        matrix = [range(zz,zz + l1 + 1) for zz in xrange(l2 + 1)]
        for zz in xrange(0,l2):
            for sz in xrange(0,l1):
                if s1[sz] == s2[zz]:
                    matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz])
                else:
                    matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz] + 1)
        return matrix[l2][l1]

x =  np.array(['ape', 'appel', 'apple', 'peach', 'puppy'])

km = mlpy.Kmedoids(k=3, dist=distance())
medoids,clusters,a,b = km.compute(x)

print medoids
print clusters
print a

print x[medoids] 
for i,c in enumerate(x[medoids]):
    print "medoid", c
    print x[clusters[a==i]]
