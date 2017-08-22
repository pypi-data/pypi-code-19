#!/usr/bin/env python

from setuptools import setup

setup(
    name='kfront',
    version='0.0.1',
    description='A library for using the Knowledge Front monitoring REST API',
    author='Dan Porter',
    author_email='dpreid@gmail.com',
    url='https://github.com/Stealthii/python-kfront',
    packages=['kfront'],
    keywords=['knowledgefront', 'mailive', 'monitoring'],
    classifiers=[],
    install_requires=['requests'],
)
