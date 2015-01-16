import pywt, numpy as np

#print pywt.families()

data = np.ones((4,4), dtype=np.float64)
#print data
coeffs = pywt.dwt2(data, 'haar')
cA, (cH, cV, cD) = coeffs
#print cA
#print cH
#print cV

mode = 'haar'
coeffs = pywt.wavedec([1,2,3,4,5,6,7,8], mode, level=3)
print coeffs
coeffs_H = list(coeffs)
coeffs_H[0] = np.zeros(coeffs_H[0].shape)
print pywt.waverec2(coeffs_H, mode)



