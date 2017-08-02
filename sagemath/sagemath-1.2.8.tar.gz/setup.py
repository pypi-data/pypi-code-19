## -*- encoding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages
from codecs import open # To open the README file with proper encoding

# Get information from separate files (README, VERSION)
def readfile(filename):
    with open(filename,  encoding='utf-8') as f:
        return f.read()

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]

setup(
    name = "sagemath",
    version = readfile("VERSION"), # the VERSION file is shared with the documentation
    description='A free open-source mathematics software system',
    long_description = readfile("README.rst"), # get the long description from the README
    url='https://www.sagemath.org',
    author='The Sage Development Team',
    author_email='marc.masdeu@gmail.com', # choose a main contact email
    packages=find_packages(),
    license='GPLv3+', # This should be consistent with the LICENCE file
    classifiers=[
      # How mature is this project? Common values are
      #   3 - Alpha
      #   4 - Beta
      #   5 - Production/Stable
      'Development Status :: 5 - Production/Stable',
      'Intended Audience :: Science/Research',
      'Topic :: Scientific/Engineering :: Mathematics',
      'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
      'Programming Language :: Python :: 2.7',
    ], # classifiers list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords = "SageMath",
    install_requires = REQUIREMENTS
)
