#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import glossario

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = glossario.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on Bitbucket:")
    os.system("hg tag -m 'version %s' %s" % (version, version))
    os.system("hg push")
    sys.exit()


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

readme = read('README.rst')
history = read('HISTORY.rst').replace('.. :changelog:', '')

setup(
    name='django-glossa',
    version=version,
    description="""A glossary app for Django""",
    long_description=readme + '\n\n' + history,
    author='GS1 Italy',
    author_email='ict@gs1it.org',
    url='https://bitbucket.org/gs1it/django-glossa',
    packages=[
        'glossario',
    ],
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='django-glossa',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Natural Language :: Italian',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
    ],
)
