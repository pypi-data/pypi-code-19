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


from setuptools import setup

from hdgfrom import __VERSION__


setup(name="hdgfrom",
      version=__VERSION__,
      description="Generate HDG files for GEMSS",
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
          "Development Status :: 2 - Pre-Alpha",
          "Environment :: Console",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Operating System :: MacOS :: MacOS X",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 3",
          "Topic :: Scientific/Engineering :: Artificial Intelligence"
      ]
     )
