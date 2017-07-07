#!/usr/bin/python
"""

"""
import numpy as np
import time
import h5py
import sys
import os

from larch import Group, ValidateLarchPlugin

def read_xrd_hdf5(fname, verbose=False, _larch=None):
    # Reads a HDF5 file created for XRD mapping
    
    t0 = time.time()
    h5file = h5py.File(fname, 'r')

    ## f['entry/data/data'] & f['entry/instrument/detector/data'] are same values
    xrd_data = h5file['entry/instrument/detector/data'].value

    ## Forces data into 3D shape
    shape = xrd_data.shape ## (no_images,pixels_x,pixels_y)
    if len(shape) == 2:
        print('Reshaping to (%i, %i, %i)' % (1, shape[0], shape[1]))
        xrd_data.shape = (1, shape[0], shape[1])

    return xrd_data

def test_read(fname):
    print( fname,  os.stat(fname))
    fd = read_xrd_hdf5(fname, verbose=True)
    print(fd.counts.shape)

def registerLarchPlugin():
    return ('_xrd', {'read_xrd_hdf5': read_xrd_hdf5})
