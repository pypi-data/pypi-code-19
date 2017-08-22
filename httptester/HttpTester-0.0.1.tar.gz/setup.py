#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="HttpTester",
    version="0.0.1",
    author="Inflower",
    author_email="inflowers@126.com",
    description="a http state tester",
    long_description=open("README.rst").read(),
    license="MIT",
    url="https://pypi.python.org/pypi/httptester",
    packages=['HttpTester'],
    install_requires=[
        "requests"
        ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)