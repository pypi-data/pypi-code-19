#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 18:07:44 2017

@author: alex
"""

from setuptools import setup, find_packages
 
 
 
setup(name='PS_TIFF_Reader',
 
      version='0.1',
  
      author='alex',
 
      author_email='alex@parkafm.co.kr',
 
      description='TIFF FILE READER',
 
      packages=find_packages(exclude=['tests']),
 

 
      zip_safe=False,
 
      )
