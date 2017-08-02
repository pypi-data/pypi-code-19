#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from os.path import join, dirname
import threebot_repeat as app


def long_description():
    try:
        return open(join(dirname(__file__), 'README.md')).read()
    except IOError:
        return "LONG_DESCRIPTION Error"


setup(
    name='threebot-repeat',
    version=app.__version__,
    description='Add repetitive Task management to you 3bot',
    long_description=long_description(),
    author='arteria GmbH',
    author_email='admin@arteria.ch',
    packages=['threebot_repeat'],
    install_requires=open('requirements.txt').read().split('\n'),
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta',
    ]
)
