import numpy as np
import pywt
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.cm as cm

#http://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_matplotlib_rgb_brg_image_load_display_save.php

file_img = '/home/janson/download/z2.jpg'

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

def thumbnail(infile='/home/janson/download/z.jpg'):
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
        print img.size
        for i in range(img.size[0]):    # for every pixel:
            for j in range(img.size[1]):
                x = [0,0,0]
                x[pos] = int(rlt[i][j])
                pixels[i,j] = (x[0],x[1],x[2])
        img.show()

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
    paint_img(imArray_H)
    #imgplot = plt.imshow(imArray_H.T)
    #plt.show()

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
    fname = '/home/janson/download/z2.png'
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
            r,g,b =  pixels[i,j]
            arr_r[i,j] = r
            arr_g[i,j] = g
            arr_b[i,j] = b
    return arr_r,arr_g,arr_b

def trans(imArray, mode='haar', level=1):
    coeffs = pywt.wavedec2(imArray, mode, level=level)
    coeffs_H = list(coeffs)
    coeffs_H[0] = np.zeros(coeffs_H[0].shape)
    imArray_H = pywt.waverec2(coeffs_H, mode)
    return imArray_H

def test_02(img):
    ar,ag,ab = im2arr_3(img)
    tar,tag,tab = trans(ar), trans(ag), trans(ab)
    paint_img(tar, pos=0)
    paint_img(tag, pos=1)
    paint_img(tab, pos=2)
    img = Image.new('RGB', tar.shape, "black")
    pixels = img.load()
    for i in range(img.size[0]):    # for every pixel:
        for j in range(img.size[1]):
            pixels[i,j] = (int(tar[i][j]), int(tag[i][j]), int(tab[i][j]))
            print pixels[i,j]
    img.show()

#thumbnail()
#print im2arr(file_img)
#wtHighFreq(file_img)
#paint(file_img)
#paint2()
#new_img()

test_02(file_img)

