import numpy as np


def rebin(a, newshape):
    """Rebin an array to a new shape."""
    assert len(a.shape) == len(newshape)

    slices = [slice(0, old, float(old) / new) for old, new in zip(a.shape, newshape)]
    coordinates = np.mgrid[slices]
    indices = coordinates.astype('i')  # choose the biggest smaller integer index
    print(len(indices), indices.max())
    return a[tuple(indices)]


def rebin_factor(a, newshape):
    '''Rebin an array to a new shape.
    newshape must be a factor of a.shape.
    '''
    assert len(a.shape) == len(newshape)
    assert not np.sometrue(np.mod(a.shape, newshape))

    slices = [slice(None, None, old / new) for old, new in zip(a.shape, newshape)]
    return a[slices]
