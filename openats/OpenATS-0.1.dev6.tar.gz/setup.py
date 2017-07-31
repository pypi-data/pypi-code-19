#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import unicode_literals
import os
import sys

from setuptools import setup, find_packages

# ============================================
APP_NAME = 'OpenATS'
REPOSITORY_NAME = 'OpenATS'
# ============================================

entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      ats-init = OpenATS.commands:init
      ats-makeDataset = OpenATS.commands:makeDataset
      ats-run = OpenATS.commands:run
      ats-runAll = OpenATS.commands:runAll
    """
# ============================================

try:
    with open('README.rst') as f:
        readme = f.read()
except IOError:
    readme = ''

try:
   import pypandoc
   readme = pypandoc.convert('README.md', 'rst')
   readme = readme.replace("\r","")
except Exception as err:
   readme = "Oops!  That was no valid number.  Try again..."
   readme += "Unexpected error:{}".format(sys.exc_info()[0])
   readme += " error: {0}".format(err)


def _requires_from_file(filename):
    return open(filename).read().splitlines()

# version
here = os.path.dirname(os.path.abspath(__file__))
version = next((line.split('=')[1].strip().replace("'", '')
                for line in open(os.path.join(here, APP_NAME, '__init__.py'))
                if line.startswith('__version__ = ')), '0.0.dev0')

# ============================================


setup(
    name=APP_NAME,
    version=version,
    url='https://github.com/peace098beat/'+APP_NAME,
    author='FiFi',
    author_email='fifi@example.jp',
    maintainer='FiFi',
    maintainer_email='fifi@example.jp',
    description='Open AI Training Station for Keras',
    long_description=readme,
    packages=find_packages(),
    install_requires=_requires_from_file('requirements.txt'),
    license="MIT",
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points=entry_points,
)