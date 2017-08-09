#!/usr/bin/env python

import pycamhd.lazycache as camhd
import numpy as np
from PIL import Image

# remote file
filename = '/RS03ASHS/PN03B/06-CAMHDA301/2016/11/13/CAMHDA301-20161113T000000Z.mov'
test_lazycache = 'https://camhd-app-dev-nocache.appspot.com/v1/org/oceanobservatories/rawdata/files'

def test_get_frame_np():
    # download moov_atom from remote file
    img = camhd.get_frame( test_lazycache + filename, 5000 )

    assert isinstance( img, np.ndarray )

    shape = img.shape
    assert shape[1] == 1920
    assert shape[0] == 1080


def test_get_frame_image():

    for format in ['png', 'jpeg', 'jpg']:
        # download moov_atom from remote file
        img = camhd.get_frame( test_lazycache + filename, 5000, format = format )

        assert isinstance( img, Image.Image )

        ## PIL only knows "JPEG"
        format = "jpeg" if format == 'jpg' else format

        assert img.format == format.upper()

        shape = img.size
        assert shape[0] == 1920
        assert shape[1] == 1080


## Object-oriented version
def test_get_frame_np_oo():
    r = camhd.lazycache()
    img = r.get_frame( filename, 5000 )

    assert isinstance( img, np.ndarray )

    shape = img.shape
    assert shape[1] == 1920
    assert shape[0] == 1080


## Test file can be run as a standalone.  Why?  Was diagnosing segfaults
# and some of the debug output was being hidden by pytest
if __name__ == "__main__":
    test_get_frame_image()
