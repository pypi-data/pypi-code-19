#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

from setuptools import setup
from setuptools import find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

setup(
    name='git-lazy',
    version='0.2.1',
    description="Sync repos across development environments. Bulk status|push|pull operations on git repos.",
    long_description=readme + '\n\n' + history,
    author="Tim Santor",
    author_email='tsantor@xstudios.agency',
    url='https://bitbucket.org/tsantor/git-lazy',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    include_package_data=True,
    install_requires=[
        'python-bash-utils',
        'six',
    ],
    license="MIT",
    keywords='git-lazy',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points={
        'console_scripts': [
            'git-lazy = gitlazy.gitlazy:run',
        ],
    },
)
