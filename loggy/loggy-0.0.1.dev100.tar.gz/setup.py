#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = '0.0.1.dev100'

setup(
    name = 'loggy',
    description = 'A simplified logging utility for Python.',
    license = 'MIT',
    classifiers = [
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'Topic :: System :: Logging',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],
    version = VERSION,
    packages = find_packages(),
    url = 'https://github.com/jmei91/loggy',
    author = 'Jie Mei',
    author_email = 'mei.jie@hotmail.com',
    )
