#!/usr/bin/env python

# Copyright 2011-2012 Eric Wendelin
#
# This is free software, licensed under the Apache License, Version 2.0,
# available in the accompanying LICENSE.txt file.

#from distutils.core import setup
from setuptools import setup
import sys

sys.path.append('lcov_cobertura')
import lcov_cobertura

setup(name='lcov_cobertura_fix',
    version='1.6.1a2',
    description='Fix for LCOV to Cobertura XML converter',
    url='https://github.com/gberenice/lcov-cobertura-fix/',
    long_description=lcov_cobertura.LcovCobertura.__doc__,
    package_dir={'': 'lcov_cobertura'},
    provides=['lcov_cobertura'],
    py_modules=['lcov_cobertura'],
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Intended Audience :: Developers',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 3',
                 'License :: OSI Approved :: Apache Software License',
                 'Topic :: Software Development :: Testing',
                 'Topic :: Software Development :: Quality Assurance'
    ],
    keywords='lcov cobertura',
    entry_points={
        'console_scripts': ['lcov_cobertura=lcov_cobertura:main']
    },
    license='Apache License, Version 2.0'
)
