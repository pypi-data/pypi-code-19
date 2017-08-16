"""
 # Copyright (c) 2017 Boolein Integer Indonesia, PT.
 # suryakencana 2/17/17 @author nanang.suryadi@boolein.id
 #
 # You are hereby granted a non-exclusive, worldwide, royalty-free license to
 # use, copy, modify, and distribute this software in source code or binary
 # form for use in connection with the web services and APIs provided by
 # Boolein.
 #
 # As with any software that integrates with the Boolein platform, your use
 # of this software is subject to the Boolein Developer Principles and
 # Policies [http://developers.boolein.com/policy/]. This copyright notice
 # shall be included in all copies or substantial portions of the software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 # THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 # FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 # DEALINGS IN THE SOFTWARE
 # 
 # setup.py
"""

# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import re
from codecs import open
from setuptools import setup, find_packages
from setuptools.command.test import test as _test

###############################################################################

NAME = 'baka_model'
DESC = 'Baka: Skeleton framework built top of pyramid, baka_model for sqlalchemy'
AUTHOR = 'Nanang Suryadi'
AUTHOR_EMAIL = 'nanang.jobs@gmail.com'
URL = 'https://github.com/suryakencana/baka_model'
DOWNLOAD_URL = 'https://github.com/suryakencana/baka_model/archive/0.17.1.tar.gz'
LICENSE = 'MIT'
KEYWORDS = ['model', 'sqlalchemy', 'framework']
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Framework :: Pyramid',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Operating System :: OS Independent',
]
INSTALL_REQUIRES = [
    'setuptools',
    'pyramid',
    'sqlalchemy',
    'zope.sqlalchemy',
    'psycopg2',
    'python-dateutil',
    'transaction',
    'pyramid_tm',
    'sqlalchemy_utils',
    'awesome-slugify',
    'python-dateutil',
    'bcrypt',
]
EXTRAS_REQUIRE = {}
ENTRY_POINTS = {}

###############################################################################

HERE = os.path.abspath(os.path.dirname(__file__))
VERSION_FILE = os.path.join(HERE, 'baka_model', '__init__.py')
LONGDESC_FILE = os.path.join(HERE, 'README.rst')

with open(LONGDESC_FILE, encoding='utf-8') as fp:
    LONGDESC = fp.read()


def get_version():
    """Extract package __version__"""
    with open(VERSION_FILE, encoding='utf-8') as fp:
        content = fp.read()
    match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', content, re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Could not extract package __version__")


class test(_test):
    def run(self):
        print('please run tox instead')

setup(name=NAME,
      version=get_version(),
      description=DESC,
      long_description=LONGDESC,
      classifiers=CLASSIFIERS,
      keywords=KEYWORDS,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      download_url=DOWNLOAD_URL,
      license=LICENSE,
      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,
      entry_points=ENTRY_POINTS,
      cmdclass={'test': test},
      packages=find_packages(include=['baka_model', 'baka_model.*']),
      zip_safe=False)
