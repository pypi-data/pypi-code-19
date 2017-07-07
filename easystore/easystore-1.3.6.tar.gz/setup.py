#!/usr/bin/env python

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

REQUIREMENTS = [
]

setup(
    name='easystore',
    version='1.3.6',
    description='Redis like syntax to store and retrieve from json files',
    long_description=README,
    author='Shomiron DAS GUPTA',
    author_email='shomiron@netmonastery.com',
    url='https://github.com/shomiron/easystore',
    license="Apache",
    install_requires=REQUIREMENTS,
    keywords=['redis', 'json'],
    packages=['easystore'],
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
)
