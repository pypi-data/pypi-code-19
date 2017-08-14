#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '1.0.0'


LONG_DESCRIPTION = open('README.rst').read()

setup(
    name="djdg-django-oauth",
    version=version,
    description="djdg OAuth2 method for Django",
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Framework :: Django :: 1.9",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='djdg django oauth2 oauthlib',
    author="zaneYang",
    author_email='zane.yang@hey900.com',
    license='BSD',
    packages=find_packages(),
    install_requires=[
        'django>=1.9',
        'six',
        'simplejson',
    ],
    zip_safe=False,
)
