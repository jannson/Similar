import numpy as np
import pywt
from PIL import Image
import colorsys
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.cm as cm
import matplotlib.rcsetup as rcsetup

print matplotlib.matplotlib_fname()
print(rcsetup.all_backends)

#http://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_matplotlib_rgb_brg_image_load_display_save.php
#http://stackoverflow.com/questions/7534453/matplotlib-does-not-show-my-drawings-although-i-call-pyplot-show

file_img = '/home/janson/downloads/z2.jpg'

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.144])

def im2array(img, dtype='float'):
    im = Image.open(img)
    return np.asarray(im, dtype=dtype)

def im2arr(img):
    im = Image.open(img)
    row,col =  im.size
    data = np.zeros([row, col])
    #im.show()
    pixels = im.load()
    for i in range(row):
        for j in range(col):
            r,g,b =  pixels[i,j]
            data[i,j] = r
    return data

def thumbnail(infile='/home/janson/downloads/z.jpg'):
    try:
        img = Image.open(infile)
        size = (128,128)
        img.thumbnail(size, Image.ANTIALIAS)
        img.save(file_img, "JPEG")
    except IOError:
        print "cannot create thumbnail for '%s'" % infile
        return None

def paint_img(rlt, pos=0):
    if len(rlt.shape) == 2:
        img = Image.new('RGB', rlt.shape, "black")
        pixels = img.load()
        for i in range(img.size[0]):    # for every pixel:
            for j in range(img.size[1]):
                x = [0,0,0]
                x[pos] = int(rlt[i][j])
                x[0],x[1],x[2] = yiq2rgb(x[0],x[1],x[2])
                pixels[i,j] = (x[0],x[1],x[2])
        img.show()

def rgb2yiq(x,y,z):
    return colorsys.rgb_to_yiq(float(x)/255, float(y)/255, float(z)/255)

def yiq2rgb(x,y,z):
    r = colorsys.yiq_to_rgb(x,y,z)
    return (int(r[0]*255), int(r[1]*255), int(r[2]*255))

def wtHighFreq(img, mode='haar', level=1):
    '''
    Apply Wavelet Transform to an image
    Author: Lee Seongjoo seongjoo@csai.yonsei.ac.kr
    2009 (c) Lee Seongjoo
    '''
    imArray = im2arr(img)
    # compute coefficients of multiresolution WT
    coeffs = pywt.wavedec2(imArray, mode, level=level)
    # high frequency coeffs
    coeffs_H = list(coeffs)
    #print coeffs_H[0].shape
    # discarding the low frequency
    # Approximation coeffs are from the low-pass filter
    coeffs_H[0] = np.zeros(coeffs_H[0].shape)
    # multilevel reconstruction
    imArray_H = pywt.waverec2(coeffs_H, mode)
    #paint_img(imArray_H)
    imgplot = plt.imshow(imArray_H.T)
    plt.show()

def paint(img):
    rlt = im2array(img)
    (x,y,z) = rlt.shape
    for i in range(x):
        for j in range(y):
            rlt[i][j][1] = 0
            rlt[i][j][2] = 0

    imgplot = plt.imshow(rlt)
    #fname = 'cartoon.png'
    #image = Image.open(fname).convert("L")
    #arr = np.asarray(image)
    #plt.imshow(arr, cmap = cm.Greys_r)
    plt.show()

def paint2():
    fname = '/home/janson/downloads/z2.png'
    image = Image.open(fname).convert("L")
    arr = np.asarray(image)
    plt.imshow(arr, cmap = cm.Greys_r)
    plt.show()

def new_img():
    img = Image.new( 'RGB', (255,255), "black")
    pixels = img.load()
    for i in range(img.size[0]):    # for every pixel:
        for j in range(img.size[1]):
            pixels[i,j] = (i, j, 100) # set the colour accordingly
    img.show()

def im2arr_3(img):
    im = Image.open(img)
    row,col =  im.size
    arr_r,arr_g,arr_b = (np.zeros([row, col]), np.zeros([row, col]), np.zeros([row, col]))
    pixels = im.load()
    for i in range(row):
        for j in range(col):
            r,g,b =  rgb2yiq(*pixels[i,j])
            arr_r[i,j] = r
            arr_g[i,j] = g
            arr_b[i,j] = b
    return arr_r,arr_g,arr_b

def trans(imArray, mode='haar', level=1):
    coeffs = pywt.wavedec2(imArray, mode, level=level)
    coeffs_H = list(coeffs)
    coeffs_H[0] = np.zeros(coeffs_H[0].shape)
    imArray_H = pywt.waverec2(coeffs_H, mode)
    #return imArray
    #print "img1", imArray[0]
    #print "img2", imArray_H[0]
    return imArray_H

def test_02(img):
    ar,ag,ab = im2arr_3(img)
    tar,tag,tab = trans(ar), trans(ag), trans(ab)
    #paint_img(tar, pos=0)
    #paint_img(tag, pos=1)
    #paint_img(tab, pos=2)
    #img = Image.new('RGB', tar.shape)
    #pixels = img.load()
    pixels = np.zeros((tar.shape[0], tar.shape[1], 3))
    for i in range(tar.shape[0]):    # for every pixel:
        for j in range(tar.shape[1]):
            r,g,b = yiq2rgb(tar[i][j], tag[i][j], tab[i][j])
            #pixels[i,j] = (r,g,b)
            pixels[i,j] = [r,g,b]
            #print pixels[i,j]
    #img.show()
    imgplot = plt.imshow(pixels)
    plt.show()

def test_yiq():
    a = [0,0,0,0,0,0]
    a[0] = (145, 149, 152)
    a[1] = (151, 155, 158)
    a[2] = (127, 131, 134)
    a[3] =(86, 90, 93)
    a[4] = (61, 66, 70)
    a[5] = (57, 62, 2)
    for nn in a:
        n = [float(m)/255 for m in nn]
        yiq = colorsys.rgb_to_yiq(*n)
        #r = (int(yiq[0]),int(yiq[1]),int(yiq[2]))
        rgb = colorsys.yiq_to_rgb(*yiq)
        r = (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        print n, yiq, colorsys.yiq_to_rgb(*yiq), r, nn

def test_yiq2():
    a = [0,0,0,0,0,0]
    a[0] = (145, 149, 152)
    a[1] = (151, 155, 158)
    a[2] = (127, 131, 134)
    a[3] =(86, 90, 93)
    a[4] = (61, 66, 70)
    a[5] = (57, 62, 2)
    for nn in a:
        yiq = rgb2yiq(*nn)
        r = yiq2rgb(*yiq)
        print nn, yiq, r

def test_yiq3():
    a = [0,0,0,0,0,0]
    a[0] = [145, 149, 152]
    a[1] = [151, 155, 158]
    a[2] = [127, 131, 134]
    a[3] = [86, 90, 93]
    a[4] = [61, 66, 70]
    a[5] = [57, 62, 2]

    #s = np.array([145.0, 149.0, 152.0])/255
    s = np.asarray(a, dtype='float')/255
    tranform = np.array([[0.299, 0.587, 0.114], [0.596, -0.275, -0.321], [0.212, -0.523, 0.311]])
    y = s[0]*0.299 + s[1]*0.587 + s[2]*0.114
    z = np.array([tranform[0][0], tranform[1][0], tranform[2][0]])
    #print y
    #print tranform[0], np.dot(s, z)
    #print s
    #print tranform
    print np.dot(s, tranform.T)

def test_03():
    db8 = pywt.Wavelet('db8')
    scaling, wavelet, x = db8.wavefun()

    fig, axes = plt.subplots(1, 2, sharey=True, figsize=(8,6))
    ax1, ax2 = axes

    ax1.plot(x, scaling);
    ax1.set_title('Scaling function, N=8');
    ax1.set_ylim(-1.2, 1.2);

    ax2.set_title('Wavelet, N=8');
    ax2.tick_params(labelleft=False);
    ax2.plot(x-x.mean(), wavelet);

    fig.tight_layout()


#thumbnail()
#print im2arr(file_img)
#wtHighFreq(file_img)
#paint(file_img)
#paint2()
#new_img()
test_02(file_img)
#test_yiq()
#test_03()
#test_yiq2()
#test_yiq3()

