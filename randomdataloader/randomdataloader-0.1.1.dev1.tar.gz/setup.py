#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages
import unittest

'''def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite'''

setup(
    name='randomdataloader',
    version='0.1.1.dev1',
    description='A random data loader which loads random data to a user input MySQL or sqlite3 database',
    author='gladipero',
    author_email='amar.shishodia@gmail.com',
    url='https://github.com/gladipero/Data-Loader',
    packages = ['RandomDataLoader'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: SQL',
        'Topic :: Software Development :: Testing'
        ],
    install_requires=['mysql-python','simplejson'],
    #test_suite='setup.my_test_suite',
    scripts=['bin/RandomDataLoader.py']

)
