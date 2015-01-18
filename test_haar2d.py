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
    test_haar2d()
