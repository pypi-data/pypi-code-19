# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()

requires = [
    'pyproj',
    'shapely',
    'requests'
    ]

setup(name='pyreproj',
      version='1.0.0',
      description='Python Reprojector',
      license='GPLv3+',
      long_description='\n'.join([
          README,
          '',
          'Changelog',
          '---------',
          '',
          CHANGES
      ]),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Topic :: Scientific/Engineering :: GIS",
          "Topic :: Utilities",
          "Natural Language :: English",
          "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
          "Intended Audience :: Developers",
          "Operating System :: OS Independent"
      ],
      author='Karsten Deininger',
      author_email='karsten.deininger@bl.ch',
      url='https://gitlab.com/gf-bl/pyreproj',
      keywords='web proj coordinate transformation',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires
      )
