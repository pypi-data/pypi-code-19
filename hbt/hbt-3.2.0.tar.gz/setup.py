#! /usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (C) 2017 贵阳货车帮科技有限公司
#

from setuptools import setup, find_packages

setup(
    name = "hbt",
    version = "3.2.0",
    keywords = ("pip", "rbt"),
    description = "rbt wrapper",
    long_description = "rbt wrapper for review board",
    license = "MIT Licence",

    author = "Bergkamp.Zhou",
    author_email = "zxhmilu0811@gmail.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ['RBTools>=0.7.9', 'jira>=1.0.10'],

    scripts = [],
    entry_points = {
        'console_scripts': [
            'hbt = scripts.hbt:main'
        ]
    }
)