# coding: utf-8

try:
    import setuptools
    from setuptools import setup, find_packages
except ImportError:
    print("Please install setuptools.")

import os
long_description = 'a data browser which has a tree structure'

setup(
    name  = 'jupyterhack',
    version = '0.0',
    description = 'Visualizing data in a tree structure',
    long_description = long_description,
    license = 'MIT',
    author = 'Yuki Arai',
    author_email = 'threemeninaboat3247@gmail.com',
    url = 'https://github.com/threemeninaboat3247/jupyterhack',
    keywords = 'data browser',
    packages = find_packages(),
    install_requires = ['numpy','matplotlib','pandas'],
    classifiers = [
      'Programming Language :: Python :: 3.5',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: MIT License'
    ]
)
