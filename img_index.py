import os
import math
import numpy as np
from PIL import Image, ImageOps
from haar2d import haar2d, ihaar2d

file_dir = '/home/janson/downloads/testimg'
thumb = 'thumb'

def thumbnail(infile):
    try:
        img = Image.open(infile)
        size = (128,128)
        #img.thumbnail(size, Image.ANTIALIAS)
        thub = ImageOps.fit(img, size, Image.ANTIALIAS)

        file_img = infile.split('/')[-1]
        thub.save(os.path.join(file_dir, thumb, file_img), "JPEG")
    except IOError:
        print "cannot create thumbnail for '%s'" % infile
        return None

def thumb_all():
    data_dir = file_dir
    for d in os.listdir(data_dir):
        f = os.path.join(data_dir, d)
        if os.path.isfile(f) and d.endswith(".jpeg"):
            thumbnail(f)

dbspace = {"sigs":{}, 'buckets':None}
dbspace["buckets"] = [[[[] for k in range(128*128)] for j in range(2)] for i in range(3)]
num_coefs = 40

weights = np.array([[5.00, 19.21, 34.37], [0.83,  1.26,  0.36], [ 1.01,  0.44,  0.45], \
                    [ 0.52,  0.53,  0.14], [ 0.47,  0.28,  0.18], [ 0.30,  0.14,  0.27]])
img_bin = [5] * 128 * 128
for i in range(5):
    for j in range(5):
        img_bin[i*128 + j] = max(i,j)

def index_image(id, img_file):
    img = Image.open(img_file)
    size = (128,128)
    im = img.resize(size)

    arr = np.asarray(im, dtype='float')
    row, col = arr.shape[0], arr.shape[1]
    tranform = np.array([[0.299, 0.587, 0.114], [0.596, -0.275, -0.321], [0.212, -0.523, 0.311]])
    arr = np.dot(arr, tranform.T)

    images = [arr[:,:,:1].reshape(row, col), arr[:,:,1:2].reshape(row, col), arr[:,:,2:].reshape(row, col)]
    avgl = []
    haars = []
    colors = 3
    num_coefs = 40
    imgbuckets = dbspace["buckets"]

    for i in range(colors):
        haar = haar2d(images[i]).reshape(row*col)
        avgl.append(haar[0]/(256*128))
        haar[0] = 0.0

        ind = np.argpartition(np.absolute(haar), 0-num_coefs)[-num_coefs:]
        haar = haar[ind]
        small = (haar <= 0)
        big = (haar > 0)
        origin_small = ind[small]
        origin_big = ind[big]
        #print "i is :", i, "neg is:"
        #print origin_small
        #print "pos is :"
        #print origin_big
        for j in origin_small:
            imgbuckets[i][0][j].append(id)
        for j in origin_big:
            imgbuckets[i][1][j].append(id)

    print avgl
    dbspace["sigs"][id] = avgl

def query_img(img):
    imgbuckets = dbspace["buckets"]
    sigs = dbspace["sigs"]

    #TODO do in a function
    im2 = Image.open(img)
    im = im2.resize((128,128))
    arr = np.asarray(im, dtype='float')
    row, col = arr.shape[0], arr.shape[1]
    tranform = np.array([[0.299, 0.587, 0.114], [0.596, -0.275, -0.321], [0.212, -0.523, 0.311]])
    arr = np.dot(arr, tranform.T)

    images = [arr[:,:,:1].reshape(row, col), arr[:,:,1:2].reshape(row, col), arr[:,:,2:].reshape(row, col)]
    avgl = []
    haars = []
    colors = 3
    num_coefs = 40
    img_sig = [[0]*2 for i in range(colors)]

    for i in range(colors):
        haar = haar2d(images[i]).reshape(row*col)
        avgl.append(haar[0]/(256*128))
        haar[0] = 0.0

        ind = np.argpartition(np.absolute(haar), 0-num_coefs)[-num_coefs:]
        haar = haar[ind]
        small = (haar <= 0)
        big = (haar > 0)
        img_sig[i][0] = ind[small]
        img_sig[i][1] = ind[big]

    scores = {}
    for id,sig in sigs.items():
        scores[id] = 0.0
        for c in range(colors):
            scores[id]  = scores[id] + (weights[0][c] * math.fabs(sig[c] - avgl[c]))

    for pn in range(2):
        for c in range(colors):
            for idx in img_sig[c][pn]:
                for uit in imgbuckets[c][pn][idx]:
                    scores[uit] = scores[uit] - weights[img_bin[idx]][c]

    scores = sorted(scores.items(), key = lambda item: -item[1])
    results = []
    for k,v in scores:
        results.append(k)
        results.append(v)
    return normalizeResults(results)

def normalizeResults(results):
    res = []
    for i in range(len(results) / 2):
        rid = long(results[i*2])
        rsc = results[i*2+1]
        rsc = -100.0*rsc/38.70  # normalize
        #sanity checks
        if rsc<0:rsc = 0.0
        if rsc>100:rsc = 100.0
        res.append([rid,rsc])

    res.reverse()
    return res

def index_all():
    #data_dir = os.path.join(file_dir, thumb)
    data_dir = "/opt/projects/source/iLab/dataset/demo1"
    for d in os.listdir(data_dir):
        f = os.path.join(data_dir, d)
        if os.path.isfile(f) and d.endswith(".jpg"):
            id = int(f.split('/')[-1].split('.')[0])
            index_image(id, f)

def trans_img(infile):
    try:
        img = Image.open(infile)
        size = (128,128)
        im1 = img.resize(size)
        im1.show()
    except IOError:
        print "cannot create thumbnail for '%s'" % infile
        return None

#img_file = '/home/janson/downloads/z3.jpg'
#thumb_all()
#index_image(1, img_file)
index_all()
print query_img('/opt/projects/source/iLab/dataset/demo1/1.jpg')
#trans_img('/home/janson/downloads/z3.jpg')
