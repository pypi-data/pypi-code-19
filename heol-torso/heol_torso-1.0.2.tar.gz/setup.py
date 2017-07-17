#!/usr/bin/env python
# coding: utf8

import re
import sys

from setuptools import setup, find_packages


def version():
    with open('heol_torso/_version.py') as f:
        return re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read()).group(1)


extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

# poppy-creature is a placeholder to avoid breaking code examples
# all its code is now in pypot
extra_packages = []
try:
    import poppy.creatures

    extra_packages.append('poppy-creature >= 2.0')
except ImportError:
    pass

setup(name='heol_torso',
      version=version(),
      packages=find_packages(),

      install_requires=['pypot >= 3.0'] + extra_packages,

      include_package_data=True,
      exclude_package_data={'': ['README', '.gitignore']},

      zip_safe=False,

      author='Alexandre Le Falher, Florian RUEN',
      author_email='florian.ruen@gmail.com',
      description='Heol Software Library',
      url='https://github.com/Heolrobotics/Heol-torso',
      license='GNU GENERAL PUBLIC LICENSE Version 3',

      **extra
      )
