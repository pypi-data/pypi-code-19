#!/usr/bin/env python

import sys
import os
import codecs

from setuptools import setup, find_packages


__dir__ = os.path.abspath(os.path.dirname(__file__))

# To prevent a redundant __version__, import it from the packages
sys.path.insert(0, __dir__)

try:
    from objecttools import __version__, __author__, __email__
finally:
    sys.path.pop(0)

with codecs.open(os.path.join(__dir__, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

from setuptools.command.sdist import sdist as _sdist
class sdistzip(_sdist):
    def initialize_options(self):
        _sdist.initialize_options(self)
        self.formats = 'zip'

setup_args = dict(
    cmdclass={'sdist': sdistzip},
    name='objecttools',

    version=__version__,

    description='Various tools for working with objects and classes in Python',
    long_description=long_description,

    url='https://github.com/MitalAshok/objecttools',

    author=__author__,
    author_email=__email__,

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    platforms=['any'],

    keywords=['library', 'cached', 'properties', 'singletons'],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=[],
    extras_require={},
    entry_points={},

    test_suite='tests'
)


setup(**setup_args)
