#!/usr/bin/env python

#
# HDG_from -- Generate HDG files for GEMSS
#
# Copyright (C) 2017 Di WU
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.
#

# Compatibility with Python 2.7
from __future__ import absolute_import, division, print_function, unicode_literals

from setuptools import setup

from hdgfrom import __VERSION__


def readme():
    with open("README.rst") as readme_file:
        return readme_file.read()


setup(name="hdgfrom",
      version=__VERSION__,
      description="Generate HDG files for GEMSS",
      long_description=readme(),
      author="Di Wu",
      author_email="di.wu@ntnu.no",
      url="https://github.com/wudi312858/hdg-from",
      license="LICENSE.txt",
      packages=["hdgfrom"],
      test_suite="tests",
      entry_points = {
        "console_scripts": [
            "hdg-from = hdgfrom.cli:main"
        ]
      },
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: Console",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Operating System :: MacOS :: MacOS X",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Topic :: Scientific/Engineering"
      ]
     )
