#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='dojo-mysql',
    version='0.0.29',
    description='Dojo source and sink adapters for MySQL connections.',
    author='Data Up',
    author_email='dojo@dataup.me',
    url='https://dojo.dataup.me/',
    packages=find_packages(exclude=['tests', '.cache', '.venv', '.git', 'dist']),
    install_requires=[
        'dojo',
        'PyMySQL'
    ]
)
