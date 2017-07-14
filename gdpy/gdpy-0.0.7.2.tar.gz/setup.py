#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = '0.0.7.2'

setup(
    name='gdpy',
    version=version,
    description='GeneDock Official Python SDK',
    # long_description=readme,
    packages=['gdpy'],
    install_requires=[
        'PyYAML==3.11',
        'requests==2.5.3'
    ],
    include_package_data=True,
    url="https://www.genedock.com",
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
