#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script for installing xfcsdashboard.

To install, run:

    python setup.py install

"""

# Modified from https://github.com/pypa/sampleproject/blob/master/setup.py

from setuptools import setup, find_packages
from codecs import open
from os import path
import sys

from xfcsdashboard.version import VERSION

if sys.argv[-1] == 'setup.py':
    print("To install xfcsdashboard, run 'python setup.py install'\n")

if sys.version_info[:3] < (3, 5):
    print('xfcsdashboard requires Python 3.5 or later ({}.{}.{} detected)'.format(*sys.version_info[:3]))
    sys.exit(-1)


here = path.abspath(path.dirname(__file__))


setup(
    name='xfcsdashboard',
    version=VERSION,
    description='Creates interactive plots for FCS file metadata (3.0, 3.1).',
    long_description=open('README.rst').read(),
    url='https://github.com/j4c0bs/xfcsdashboard',
    author='Jeremy Jacobs',
    author_email='pub@j4c0bs.net',
    license='BSD',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'
    ],

    keywords='FCS FCS3.0 FCS3.1 flow cytometry dashboard',
    packages=find_packages(),
    python_requires='>3.5',
    install_requires=['pandas', 'plotly>=2.0.12'],
    extras_require={},
    package_data={'':['LICENSE.txt', 'MANIFEST.in']},
    data_files=[],
    entry_points={
        'console_scripts': [
            'xfcsdashboard=xfcsdashboard.command:main'
        ],
    },
)
