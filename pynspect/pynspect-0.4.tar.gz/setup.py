#!/usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Copyright (c) since 2016, CESNET, z. s. p. o.
# Authors: Jan Mach <jan.mach@cesnet.cz>
#          Pavel Kácha <pavel.kacha@cesnet.cz>
# Use of this source is governed by an ISC license, see LICENSE file.
#-------------------------------------------------------------------------------

# Resources:
#   https://packaging.python.org/distributing/
#   http://python-packaging-user-guide.readthedocs.io/distributing/

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'pynspect',
    version = '0.4',
    description = 'Python 3 library for filtering, querying or inspecting almost arbitrary data structures.',
    long_description = long_description,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only'
    ],
    keywords = 'library',
    url = 'https://homeproj.cesnet.cz/git/mentat-ng.git',
    author = 'Jan Mach',
    author_email = 'jan.mach@cesnet.cz',
    license = 'MIT',
    packages = ['pynspect'],
    test_suite = 'nose.collector',
    tests_require = [
        'nose'
    ],
    install_requires=[
        'ipranges'
    ],
    zip_safe = True
)
