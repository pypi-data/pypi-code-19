#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='dojo-email',
    version='0.0.5',
    description='Dojo email drop source adapter',
    author='Data Up',
    author_email='dojo@dataup.me',
    url='https://dojo.dataup.me/',
    packages=find_packages(exclude=['tests', '.cache', '.venv', '.git', 'dist']),
    install_requires=[
        'dojo',
    ]
)
