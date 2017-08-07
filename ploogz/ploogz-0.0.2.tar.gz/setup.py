#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: setup.py
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This file is used to create the package uploaded to PyPI.
"""

from distutils.core import setup
setup(
  name='ploogz',
  packages=['ploogz'],  # This must be the same as the name above.
  version='0.0.2',
  description='A simple plugin framework',
  author='Pat Daburu',
  author_email='pat@daburu.net',
  url='https://github.com/patdaburu/ploogz',  # Use the URL to the github repo.
  download_url='https://github.com/pblair/ploogz/archive/0.0.2.tar.gz',  # I'll explain this in a second
  keywords=['plugin'],  # arbitrary keywords
  classifiers=[],
)
