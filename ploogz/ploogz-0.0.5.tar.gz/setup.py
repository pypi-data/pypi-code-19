#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: setup.py
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This file is used to create the package uploaded to PyPI.
"""

import ploogz

from distutils.core import setup
setup(
  name='ploogz',
  packages=['ploogz'],  # This must be the same as the name above.
  version=ploogz.__version__,
  install_requires=[
    'automat'
  ],
  description='A pretty simple plugin framework.',
  license='MIT',
  author='Pat Daburu',
  author_email='pat@daburu.net',
  url='http://ploogz.readthedocs.io/en/latest/index.html',  # Use the URL to the github repo.
  download_url='https://github.com/pblair/ploogz/archive/{version}.tar.gz'.format(version=ploogz.__version__),
  keywords=['plugin'],  # arbitrary keywords
  classifiers=[],
)
