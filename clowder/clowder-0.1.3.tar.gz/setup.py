#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


version = '0.1.3'

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='clowder',
    version=version,
    description = 'Client for the Clowder monitoring server',
    long_description = long_description,
    author = 'Keith Hackbarth',
    author_email = 'keith@clowder.io',
    license = 'LICENCE.txt',
    url = 'https://github.com/keithhackbarth/clowder_client',
    py_modules = ['clowder'],
    download_url = 'https://github.com/keithhackbarth/clowder_client/archive/master.zip',
    platforms='Cross-platform',
    include_package_data=True,
    zip_safe=False,
    keywords='clowder',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7'
    ],
)
