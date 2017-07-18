#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='autodocumentation',
    version='0.0.5',
    description='Some logging helpers: Context, key-value rendering, etc.',
    author='Stas Kaledin',
    author_email='staskaledin@gmail.com',
    packages=find_packages(),
    install_requires=[
        "funcsigs==1.0.2"
    ]
)