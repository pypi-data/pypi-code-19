# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import
import io
import numpy as np
import glob
from munch import Munch
from collections import OrderedDict
from datetime import datetime


def kpfm_data(fname):
    fh = io.open(fname, 'r')
    header_lines = [fh.readline()[:-1] for i in xrange(11)]
    datefmt = lambda x: datetime.strptime(x, '%m/%d/%Y %I:%M:%S %p')
    types = [
    float,
    float,
    int,
    float,
    float,
    int,
    float,
    str,
    float,
    datefmt,
    datefmt
    ]
    fh.close()

    m = Munch()

    d = OrderedDict()
    for header_line, formatter in zip(header_lines, types):
        key, val = header_line.split(": ", 1)
        d[key] = formatter(val)


    m['header'] = d

    m.x_tot = abs(d['End x [V]'] - d['Start x [V]'])
    m.y_tot = abs(d['End y [V]'] - d['Start y [V]'])

    fnames = glob.glob(fname.replace("1.", "*."))

    for i, fname_ in enumerate(fnames):

        try:
            m['ch{}'.format(i+1)] = np.loadtxt(fname_, skiprows=11)
        except:
            print("Skipping file {}".format(fname))


    dim1, dim2 = m.ch1.shape

    if m.header['Direction'] == 'y':
        Ny = dim1
        Nx = dim2
    else:
        Nx = dim1
        Ny = dim2

    m.vx = np.linspace(m.header['Start x [V]'], m.header['End x [V]'], Nx)
    m.vy = np.linspace(m.header['Start y [V]'], m.header['End y [V]'], Ny)

    return m