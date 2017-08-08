#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""

@version: 0.1
@author:  quantpy
@email:   quantpy@qq.com
@file:    setup.py
@time:    2017-08-08 22:20
"""


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__title__ = 'ebokeh'
__description__ = 'Enhanced Ebokeh, make charting much easier!'
__url__ = 'https://github.com/xbanke/ebokeh'
__version__ = '0.1'
__author__ = 'quantpy'
__author_email__ = 'quantpy@gmail.com'
__license__ = 'MIT'
__requires__ = ['bokeh', 'pandas']
__package__ = ['ebokeh', 'ebokeh/plotting']
__kewords__ = ['bokeh', 'charts']


setup(
    name=__title__,
    version=__version__,
    description=__description__,
    url=__url__,
    author=__author__,
    author_email=__author_email__,
    license=__license__,
    packages=__package__,
    keywords=__kewords__,
    install_requires=__requires__,
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ]
)

