import cv2
import numpy as np

gray = cv2.imread('test3.jpg', cv2.COLOR_BGR2GRAY);
vis = gray.copy()
#gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#vis = img.copy()
mser = cv2.MSER_create()
regions, _ = mser.detectRegions(gray)
hulls = [cv2.convexHull(p.reshape(-1, 1, 2)) for p in regions]
cv2.polylines(vis, hulls, 1, (0, 255, 0))

cv2.imshow('img', vis)
cv2.waitKey(0)
print 'aaa'
cv2.destroyAllWindows()
