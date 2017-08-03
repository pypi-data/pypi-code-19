##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""zope.browsermenu setup
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()

long_description = (read('README.rst') + '\n\n' + read('CHANGES.rst'))

TESTS_REQUIRE = [
    'zope.testing',
    'zope.testrunner',
]

setup(
    name='zope.browsermenu',
    version='4.3.0',
    url='http://github.com/zopefoundation/zope.browsermenu/',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    classifiers=[
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
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3',
    ],
    description='Browser menu implementation for Zope.',
    long_description=long_description,
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zope'],
    install_requires=[
        'setuptools',
        'six',
        'zope.browser',
        'zope.component>=3.7',
        'zope.configuration',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.pagetemplate>=3.5',
        'zope.publisher >= 4.2.1',
        'zope.schema',
        'zope.security',
        'zope.traversing>3.7',
    ],
    extras_require={
        'test': TESTS_REQUIRE,
    },
    tests_require=TESTS_REQUIRE,
    include_package_data=True,
    zip_safe=False,
)
