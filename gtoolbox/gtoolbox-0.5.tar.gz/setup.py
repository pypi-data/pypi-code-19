#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'kandit'
import os, sys
from setuptools import setup

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
#files = []

setup(name='gtoolbox',
      version='0.5',
      description='donehandle;logger;Region',
      url='http://gtoolbox',
      author='Kandit',
      author_email='girichev@planet.iitp.ru',
      license='MIT',
      packages=['gtoolbox'],
      include_package_data=True,
      zip_safe=False

)