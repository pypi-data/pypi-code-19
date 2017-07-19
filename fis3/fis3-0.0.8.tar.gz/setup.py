#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="fis3",
    version="0.0.8",
    keywords=("pip", "fis", "fis3"),
    description="扩展flask,支持fis3",
    license="MIT Licence",

    url="https://github.com/fancyboynet/pip-fis",
    author="Fancy",
    author_email="fancyboynet@gmail.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["Flask>=0.10.1", "htmlmin>=0.1.10"]
)
