#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

dependencies = ['future']

import sys

if sys.version_info.major == 2:
    dependencies.append('configparser')

setup(
    name='leryan.types',
    version='0.0.17',
    packages=find_packages(exclude=['test.*']),
    author='Florent Peterschmitt',
    author_email='florent@peterschmitt.fr',
    install_requires=dependencies,
    description='some "types": classes derived from python dict, list...',
    include_package_data=False,
    url='https://github.com/Leryan/leryan.types',
    license='MIT',
    test_suite='test',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
)
