#!/usr/bin/env python

import re
from os import path as op

from setuptools import setup


def _read(fname):
    try:
        return open(op.join(op.dirname(__file__), fname)).read()
    except IOError:
        return ''


_meta = _read('muffin_peewee_async/__init__.py')
_license = re.search(r'^__license__\s*=\s*"(.*)"', _meta, re.M).group(1)
_project = re.search(r'^__project__\s*=\s*"(.*)"', _meta, re.M).group(1)
_version = re.search(r'^__version__\s*=\s*"(.*)"', _meta, re.M).group(1)

install_requires = [
    l for l in _read('requirements.txt').split('\n')
    if l and not l.startswith('#')]

setup(
    name=_project,
    version=_version,
    license=_license,
    description="Peewee integration to Muffin framework",
    long_description=_read('README.rst'),
    platforms=['Any'],
    keywords=['muffin', 'peewee', 'peewee-async'],
    author='Marek Siarkowicz',
    author_email='serathius@protonmail.com',
    url='https://github.com/serathius/muffin-peewee-async',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    packages=['muffin_peewee_async'],
    include_package_data=True,
    install_requires=install_requires,
)
