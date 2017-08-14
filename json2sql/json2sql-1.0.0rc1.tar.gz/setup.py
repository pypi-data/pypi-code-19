#!/usr/bin/env python3
# ######################################################################
# Copyright (C) 2017  Fridolin Pokorny, fridolin.pokorny@gmail.com
# This file is part of json2sql package.
# ######################################################################

import sys
import os
from setuptools import setup


NAME = 'json2sql'


def get_requirements():
    with open('requirements.txt') as fd:
        content = fd.read().splitlines()

    return [line for line in content if not line.strip().startswith('#')]


def get_version():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'json2sql', '__init__.py')) as f:
        while True:
            line = f.readline()
            if line.startswith('__version__ = '):
                version = line[len('__version__ = ') + 1:-2]  # also remove quotes
                break
        else:
            raise ValueError("Cannot parse version information from main __init__.py")

    return version


if sys.version_info[0] != 3:
    sys.exit("Python3 is required in order to install %s" % NAME)

setup(
    name=NAME,
    version=get_version(),
    packages=[NAME],
    install_requires=get_requirements(),
    author='Fridolin Pokorny',
    author_email='fridolin.pokorny@gmail.com',
    maintainer='Fridolin Pokorny',
    maintainer_email='fridolin.pokorny@gmail.com',
    description='A lightweight Python3 library for describing SQL statements using JSON or dictionary.',
    url='https://github.com/fridex/json2sql',
    license='ASL 2.0',
    keywords='json sql tool converter',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy"
    ]
)
