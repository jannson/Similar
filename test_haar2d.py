import numpy as np
from haar2d import haar2d, ihaar2d

def test_haar2d():
    """
    Asserts the forwards and inverse wavelet transformations are correct.
    """

    assert haar2d(np.random.random([5,3]),2,debug=True).shape == (8,4), \
        "Transform data must be padded to compatible shape."

    assert haar2d(np.random.random([8,4]),2,debug=True).shape == (8,4), \
        "Transform data must be padded to compatible shape, if required."

    image = np.random.random([5,3])

    haart = haar2d(image, 3)
    haari = ihaar2d(haart, 3)[:image.shape[0], :image.shape[1]]

    assert (image - haari < 0.0001).all(), "Transform must be circular."

if __name__ == '__main__':
    #test_haar2d()

    #http://pda.readthedocs.org/en/latest/chp4.html
    # , duli de weidu
    #testarr = np.random.random([4,4]) * 10
    testarr = np.asarray([83.000000, 53.000000, 93.000000, 63.000000, 82.000000, 71.000000, 44.000000, 49.000000, 51.000000, 33.000000, 63.000000, 12.000000, 78.000000, 98.000000, 34.000000, 39.000000], dtype=float)
    testarr = testarr.reshape(4,4)
    print testarr
    a = testarr[:, :-1:2]
    b = testarr[:, 1::2]
    print (a + b) * 0.7071
    print (a - b) * 0.7071
    #print testarr[:, :1:2]
    print haar2d(testarr, 2)
