#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
file: setup.py
description: setuptools for basis
author: Luke de Oliveira (lukedeo@vaitech.io)
"""

import os
from setuptools import setup
from setuptools import find_packages


setup(
    name='basis',
    version='0.1.0',
    description=('Seamless construction of NLP pipelines involving word '
                 'vectors. Builds consistent mappings between words, integers, '
                 'and vectors, allowing you to focus on building models.'),
    author='Luke de Oliveira',
    author_email='lukedeo@vaitech.io',
    url='https://github.com/vaitech/basis',
    # download_url='https://github.com/vaitech/basis/archive/0.1.0.tar.gz',
    license='Apache 2.0',
    install_requires=['scikit-learn', 'h5py', 'six', 'spacy'],
    packages=find_packages(),
    keywords=('Machine-Learning TensorFlow Deployment Versioning Keras '
              'AWS Deep Learning'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ]
)
