#!/usr/bin/python
# -*- coding: utf-8 -*-


class ImageError(Exception):
    pass


from . import edfimage
from . import cbfimage
from . import fit2dmask
from . import numpymask
from . import esperanto
from . import mar345image


def openImage(filename):
    if filename.endswith('.edf'):
        return edfimage.EdfImage(filename)
    elif filename.endswith('.cbf'):
        return cbfimage.CbfImage(filename)
    elif filename.endswith('.msk'):
        return fit2dmask.Fit2DMask(filename)
    elif filename.endswith('.npz'):
        return numpymask.NumpyMask(filename)
    elif filename.endswith('.mar3450') or filename.endswith('.mar2300'):
        return mar345image.Mar345Image(filename)
    else:
        raise ImageError('CryIO could not recognize the image {0}'.format(filename))

open_image = openImage
