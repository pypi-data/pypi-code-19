#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import ast
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('vworker/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='vworker',
    packages=['vworker'],
    version=version,
    description='-',
    install_requires=[
        'pyfiglet',
        'ujson',
        'redis',
        'pymongo',
        'gearman'
    ],
)
