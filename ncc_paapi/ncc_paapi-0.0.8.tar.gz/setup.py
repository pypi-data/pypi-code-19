#!/usr/bin/env python3

"""NCC Performance Analyser API to ElasticSearch coupler"""

import os
from setuptools import setup

setup(
    name='ncc_paapi',
    version='0.0.8',
    description='Abstraction classes to access the PA API',
    author='NCC Group',
    license="Apache License 2.0",
    packages=['paapi'],
    install_requires=[
        'urllib3==1.19.1',
        'certifi==2017.1.23'
    ],
    url='https://github.com/ncc-tools/python-pa-api'
)
