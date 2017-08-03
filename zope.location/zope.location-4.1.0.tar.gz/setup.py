##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.location package
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()

ZCML_REQUIRES = [
    'zope.configuration',
]

COMPONENT_REQUIRES = [
    'zope.component >= 4.0.1',
]

TESTS_REQUIRE = ZCML_REQUIRES + COMPONENT_REQUIRES + [
    'zope.copy >= 4.0',
    'zope.testrunner',
]

DOCS_REQUIRE = [
    'Sphinx',
    'repoze.sphinx.autointerface',
] + ZCML_REQUIRES + COMPONENT_REQUIRES # doctest snippets need these

setup(name='zope.location',
      version='4.1.0',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Zope Location',
      long_description=(
          read('README.rst')
          + '\n\n' +
          read('CHANGES.rst')
      ),
      license='ZPL 2.1',
      keywords=('zope location structural'),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3',
      ],
      url='http://github.com/zopefoundation/zope.location/',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['zope',],
      install_requires=[
          'setuptools',
          'zope.interface>=4.0.2',
          'zope.schema>=4.2.2',
          'zope.proxy>=4.0.1',
      ],
      extras_require={
          'zcml': ZCML_REQUIRES,
          'component': COMPONENT_REQUIRES,
          'test': TESTS_REQUIRE,
          'docs': DOCS_REQUIRE,
      },
      test_suite='zope.location.tests',
      include_package_data=True,
      zip_safe=False,
)
