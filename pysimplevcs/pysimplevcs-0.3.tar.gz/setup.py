#!/usr/bin/env python
############################################################
#
# pysimplevcs
# Copyright (C) 2017, Richard Cook
# Released under MIT License
# https://github.com/rcook/pysimplevcs
#
############################################################

from __future__ import print_function
from setuptools import setup

setup(
    name="pysimplevcs",
    version="0.3",
    description="Python helpers for interacting with VCSs",
    setup_requires=["setuptools-markdown"],
    long_description_markdown_filename="README.md",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
    ],
    url="https://github.com/rcook/pysimplevcs",
    author="Richard Cook",
    author_email="rcook@rcook.org",
    license="MIT",
    packages=["pysimplevcs"],
    install_requires=["pyprelude>=0.2"],
    include_package_data=True,
    test_suite="pysimplevcs.tests.suite",
    zip_safe=False)
