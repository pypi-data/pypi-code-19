#!/usr/bin/env python
import os
import sys

from setuptools import find_packages, setup

setup(setup_requires=['pbr', 'pytest-runner>=2.9'], pbr=True, zip_safe=True)
