#!/usr/bin/env python

"""
distutils/setuptools install script.
"""
import os
import re

from setuptools import setup, find_packages


ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')


requires = [
    'requests>=2.18.1',
    'urllib3>=1.21.1'
]


def get_version():
    init = open(os.path.join(ROOT, 'stashyio', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


setup(
    name='stashyio',
    version=get_version(),
    description='The Stashy SDK for Python',
    author='Stashy',
    author_email='dev@stashyio.io',
    url='https://github.com/snclucas/stashy_python',
    download_url='https://github.com/snclucas/stashy_python',
    scripts=[],
    packages=['stashyio'],
    license="MIT",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
