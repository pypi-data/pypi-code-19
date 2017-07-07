#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

from setuptools import setup

setup(
  name='xPlotUtil',
  version='0.1.2',
  description='The program provides a GUI for the user to graph the data in different forms, normalize and fit it.',
  author='Phaulo C. Escalante',
  author_email='escalante.phaulo@outlook.com',
  url='https://github.com/AdvancedPhotonSource/xPlotUtil',
  packages=['xPlotUtil', 'xPlotUtil.Source' ],
  install_requires=['spec2nexus',
                    'matplotlib',
                    'numpy',
                    'future',
                    'peakutils',
                    ],
  license='See LICENSE File',
  platforms='any',
  scripts=['Scripts/xPlotUtil.bat', 'Scripts/xPlotUtil'],
)
