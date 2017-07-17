#!/usr/bin/env python  
from __future__ import print_function  
from setuptools import setup, find_packages  
import sys  
  
setup(  
    name="django_szuprefix",  
    version="0.1.0",  
    author="Denis Huang",  
    author_email="szuprefix@126.com",  
    description="my utils in django",  
    long_description=open("README.rst").read(),  
    license="MIT",  
    url="https://github.com/szuprefix/django_szuprefix",  
    packages=['django_szuprefix'],  
    install_requires=[  
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
        "Programming Language :: Python :: 2",  
        "Programming Language :: Python :: 2.6",  
        "Programming Language :: Python :: 2.7",  
    ],  
) 
