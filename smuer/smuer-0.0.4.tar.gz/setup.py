#!/usr/bin/env python  
from __future__ import print_function  
from setuptools import setup, find_packages  
import sys  
  
setup(  
    name="smuer",  
    version="0.0.4",  
    author="awefight",  
    author_email="547780662@qq.com",  
    description="Easy access to SMU digital platform.",  
    license="MIT",  
    url="https://github.com/awefight/smuer",  
    packages=['smuer'],  
    install_requires=[  
        "requests>=2.13.0", 
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
        "Programming Language :: Python :: 3",  
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",  
      
    ],  
)  
