from PIL import Image
import numpy

# Utils
def im2array(img, dtype='float'):
    im = Image.open(img)
    return numpy.asarray(im, dtype=dtype)

def formatimage(imArray, dtype='uint8', mode=None):
    imArray = numpy.array(imArray)

    pos_mask = numpy.array(imArray>=0, dtype='uint8')
    imArray *= pos_mask

    if dtype is 'uint8':
        upmask = numpy.array(imArray>=255, dtype=dtype)
        upmask *= 255
        downmask = numpy.array(upmask==0, dtype=dtype)

    imArray *= downmask
    imArray += upmask
    imArray = numpy.array(imArray, dtype=dtype)

    if mode is 'bw':
        binary_mask = numpy.array(imArray==255, dtype='uint8')
        imArray *= binary_mask

    image = Image.fromarray(imArray)

    return [imArray, image]
