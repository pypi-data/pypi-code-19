#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import numpy as np
import os
from os.path import abspath, dirname, join
import shutil
import sys
import tempfile
import warnings
import zipfile

import matplotlib.pylab as plt

from dclab import new_dataset
from dclab.brightness import get_brightness


def compare_bright():
    ds = new_dataset("/home/paul/Desktop/data_RTDC/rtdc_test_2/testdataset/Online/M4_0.040000ul_s.tdms")
    averages = np.zeros(len(ds), dtype=float)
    sds = np.zeros(len(ds), dtype=float)

    for ii in range(len(ds)):
        img = ds["image"][ii][:,:,0]
        cont = ds["contour"][ii]
        avg, std = get_brightness(cont=cont, img=img, ret_data="avg,sd")
        sds[ii] = std
        averages[ii] = avg
        print(avg - ds["bright_avg"][ii])

    

    plt.subplot(121)
    plt.plot(ds["bright_avg"][1:7], averages[1:7], ".")
    plt.plot([ds["bright_avg"].min(), ds["bright_avg"].max()],
             [ds["bright_avg"].min(), ds["bright_avg"].max()]
             )

    plt.subplot(122)
    plt.plot(ds["bright_sd"][1:7], sds[1:7], ".")
    plt.plot([ds["bright_sd"].min(), ds["bright_sd"].max()],
             [ds["bright_sd"].min(), ds["bright_sd"].max()]
             )

    plt.show()

if __name__ == "__main__":
    compare_bright()
    
