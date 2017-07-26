#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-sql-server-bcp',
    version='0.1.9',
    author='Exotic Objects LLC',
    author_email='git@extc.co',
    license='MIT',
    url='https://github.com/ExoticObjects/django-sql-server-bcp',
    include_package_data=True,
    long_description=open('README.md').read(),
    description='Utility for using mssql-tools BCP command with Django models',
    packages=find_packages(),
)
