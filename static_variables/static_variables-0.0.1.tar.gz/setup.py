#!/usr/bin/env python

import sys
import os
import codecs

from setuptools import setup, find_packages


__dir__ = os.path.abspath(os.path.dirname(__file__))

# To prevent a redundant __version__, import it from the packages
sys.path.insert(0, __dir__)

try:
    from static_variables import __version__, __author__, __email__
finally:
    sys.path.pop(0)

with codecs.open(os.path.join(__dir__, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup_args = dict(
    name='static_variables',

    version=__version__,

    description='Static variables for Python',
    long_description=long_description,

    url='https://github.com/MitalAshok/static_variables',

    author=__author__,
    author_email=__email__,

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        # 'Programming Language :: Python :: 2',  # Maybe someday
        # 'Programming Language :: Python :: 2.7',

        'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries'
    ],
    platforms=['any'],

    keywords=['library', 'static', 'CPython', 'code object'],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=[],
    extras_require={},
    entry_points={},

    test_suite='test'
)


setup(**setup_args)
