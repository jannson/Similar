import numpy as np
#import scipy.ndimage as nd
import math

def haar2d(image):
    assert len(image.shape) == 2, 'Must be 2D image!'

    levels = int(math.ceil(math.log(max(image.shape),2)))

    origRows, origCols = image.shape
    extraRows = 0;
    extraCols = 0;
    while (((origRows + extraRows) >> levels) << levels != (origRows + extraRows)):
        extraRows += 1
    while (((origCols + extraCols) >> levels) << levels != (origCols + extraCols)):
        extraCols += 1
    #print "Padding: %d x %d -> %d x %d" % (origRows, origCols, origRows + extraRows, origCols + extraCols)

    # Pad image to compatible shape using repitition
    rightFill = np.repeat(image[:, -1:], extraCols, axis=1)
    _image = np.zeros([origRows, origCols + extraCols])
    _image[:, :origCols] = image
    _image[:, origCols:] = rightFill
    bottomFill = np.repeat(_image[-1:, :], extraRows, axis=0)
    image = np.zeros([origRows + extraRows, origCols + extraCols])
    image[:origRows, :] = _image
    image[origRows:, :] = bottomFill
    #print "Padded image is: %d x %d" % (image.shape[0], image.shape[1])

    haarImage = image
    C = 1
    for level in range(1,levels+1):
        halfCols = (image.shape[1] >> level)
        C *= 0.7071068
        _image = image[:, :halfCols*2]

        # rows
        lowpass = (_image[:, :-1:2] + _image[:, 1::2])
        higpass = (_image[:, :-1:2] - _image[:, 1::2]) * C
        _image[:, :_image.shape[1]/2] = lowpass     # from begin to half
        _image[:, _image.shape[1]/2:] = higpass     # from half to end

        haarImage[:, :halfCols*2] = _image          # from begin to half
    haarImage[:, 0:1] = haarImage[:, 0:1] * C
    #print C
    #print 'rows complete'
    #print haarImage

    C = 1
    for level in range(1, levels+1):
        halfRows = (image.shape[1] >> level)
        C *= 0.7071068
        _image = image[:halfRows*2, :]
        #print 'col image'
        #print _image

        # cols
        lowpass = (_image[:-1:2, :] + _image[1::2, :])
        higpass = (_image[:-1:2, :] - _image[1::2, :]) * C
        _image[:_image.shape[0]/2, :] = lowpass
        _image[_image.shape[0]/2:, :] = higpass
    #print haarImage
    haarImage[0:1, :] = haarImage[0:1, :] * C

    return haarImage

def ihaar2d(image):
    assert len(image.shape) == 2, 'Must be 2D image!'

    levels = int(math.ceil(math.log(max(image.shape),2)))

    origRows, origCols = image.shape
    extraRows = 0;
    extraCols = 0;
    while (((origRows + extraRows) >> levels) << levels != (origRows + extraRows)):
        extraRows += 1
    while (((origCols + extraCols) >> levels) << levels != (origCols + extraCols)):
        extraCols += 1
    assert (extraRows, extraCols) == (0,0), 'Must be compatible shape!'

    C = 0.7071068
    for level in range(levels):
        n = 1<<level

        ek = image[:, :n].copy()
        ok = image[:, :n].copy()

        for k in range(n):
            ek[:, k] = (image[:, k] + image[:, k+n]) * C
            ok[:, k] = (image[:, k] - image[:, k+n]) * C

        image[:, 0:2*n:2] = ek
        image[:, 1:2*n+1:2] = ok

    for level in range(levels):
        n = 1<<level

        ek = image[:n, :].copy()
        ok = image[:n, :].copy()

        for k in range(n):
            ek[k, :] = (image[k, :] + image[k+n, :]) * C
            ok[k, :] = (image[k, :] - image[k+n, :]) * C

        image[0:2*n:2, :] = ek
        image[1:2*n+1:2, :] = ok

    return image
