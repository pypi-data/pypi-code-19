#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
from os.path import join

version = '0.0.5'

setuptools.setup(
  name="nteract_on_jupyter",
  version=version,
  url="https://github.com/nteract/nteract",
  author="nteract contributors",
  author_email="jupyter@googlegroups.com",
  description="Extension for the jupyter notebook server and nteract",
  packages=setuptools.find_packages(),
  include_package_data=True,
  zip_safe=False,
  install_requires=[]
)
