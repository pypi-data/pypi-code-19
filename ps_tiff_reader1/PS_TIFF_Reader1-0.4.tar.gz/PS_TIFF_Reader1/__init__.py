#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 12:28:34 2017

@author: alex
"""

import os, glob
from PS_TIFF_Reader import PS_data as ps
import matplotlib.pyplot as plt

os.chdir('/home/alex/Python_Code')
file = glob.glob('*.tiff')
z, hdr = ps.tiff_read(file[0])
plt.plot(z[0])
