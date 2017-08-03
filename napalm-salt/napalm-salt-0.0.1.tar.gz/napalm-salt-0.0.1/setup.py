#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
The setup script for napalm-logs
'''
import uuid
import codecs

from setuptools import setup, find_packages
from pip.req import parse_requirements

__author__ = 'Mircea Ulinic <mircea.ulinic@gmail.com>'

with codecs.open('README.rst', 'r', encoding='utf8') as file:
    long_description = file.read()

setup(
    name='napalm-salt',
    version='0.0.1',
    packages=find_packages(),
    author='Mircea Ulinic',
    author_email='mircea.ulinic@gmail.com',
    description='Network Automation and Programmability Abstraction Layer with Multivendor support: syslog parser',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Utilities',
        'Topic :: System :: Networking',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Intended Audience :: Developers'
    ],
    url='https://github.com/napalm-automation/napalm-salt',
    license="Apache License 2.0",
    keywords=('napalm', 'salt', 'saltstack', 'network', 'automation'),
    include_package_data=True,
)
