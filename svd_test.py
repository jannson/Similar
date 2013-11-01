# -*- coding: utf-8 -*-
from numpy import array
from numpy import eye,dot,zeros,sort
from scipy.linalg import svd,inv,eig
if __name__=='__main__':
    m=array([[1,0,0,0,2],
             [0,0,3,0,0],
             [0,0,0,0,0],
             [0,4,0,0,0]])
    #py的svd得出的d是一个数组
    u,d,vt=svd(m)
    print '---test svd---'
    print 'u',u
    print 'd',d
    print 'vt',vt
    #为了验证,构造dz矩阵,其为m*n的(4*5)
    #这里注意dz的构造方式
    dz=zeros(vt.shape[0])
    #print 'vt.shape[0]', vt.shape[0], vt.shape[1]
    dz[:len(d)]+=d
    print 'dz', dz
    #ndarray的*和matrix*是不同的,matrix的*对应dot
    print eye(len(d),vt.shape[0])*dz
    t=dot(u,eye(len(d),vt.shape[0])*dz)
    print dot(t,vt) #should be equal to m
    print '---test inv---'
    print inv(u)
    print inv(vt)
    print '---test mt*m---'
    ms=dot(m.T,m)
    print ms
    #eig可以求方阵的特征值与特征向量
    evals, evecs = eig(ms)
    #
    sevals=sort(evals)[::-1]
    v=vt.T
    print sevals
    print dz**2
    print '---test at*t=lamb_i*vi---'
    for i in range(len(sevals)):
        print dot(ms,vt[i])
        print sevals[i]*vt[i]
        print ''
 
