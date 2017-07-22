#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import beluga_py

setup(
    name='beluga_py',
    version=beluga_py.__version__,
    description="API & command-line client for BelugaCDN's API.",
    long_description=open('README.md').read(),
    author='James Addison',
    author_email='addi00+github.com@gmail.com',
    url=beluga_py.repo_url,
    license="BSD",
    packages=[
        'beluga_py'
    ],
    entry_points={
        "console_scripts": [
            "beluga = beluga_py.cli:main",
        ]
    },
    install_requires=[
        'requests',
        'six'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
