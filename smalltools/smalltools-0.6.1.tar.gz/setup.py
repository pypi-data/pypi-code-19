#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Badpasta <beforgetr@hotmail.com>
# 
# Environment:
# Python by version 2.7.

from setuptools import setup, find_packages


setup(
    name = 'smalltools',
    version = '0.6.1',
    description = 'Something simple tools in it.',
    author = 'Badpasta',
    author_email = 'beforget@hotmail.com',
    url = 'https://github.com/badpasta/smalltools',

    packages = find_packages('src'),
    package_dir = {'': 'src'},
    package_data = {'': ['*.py$']},
    install_requires = [
        'xlrd',
        'pyYaml',
    ]
    )
