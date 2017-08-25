#!/usr/bin/env python
# -*- coding: utf8 -*-

from setuptools import setup, find_packages


setup(
    name='superkwargs',
    version='0.1.0',
    author='Mihir Singh (@citruspi)',
    author_email='hello@mihirsingh.com',
    packages=find_packages(),    
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    test_suite='nose.collector',
    extras_require={
        'dev': [
            'nose',
            'coverage'
        ]
    }
)