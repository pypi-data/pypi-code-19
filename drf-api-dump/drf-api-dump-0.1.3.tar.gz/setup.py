# -*- coding: utf-8 -*-

from setuptools import setup

DESCRIPTION = """
This Django app is intended for **dump data from apps or models via HTTP**. Basically exposes
dumdata command to http.

Features:
    - Just accesible by superusers
    - Ability to include or exclude any specific app or model

Requirements:
    - Django (Developed under v1.11)
    - Django Rest Framework (Developed under v3.4.3)

More on https://github.com/davidvicenteranz/drf-api-dump/
"""

setup(
    name='drf-api-dump',
    version='0.1.3',
    author='David Vicente Ranz',
    author_email='dvicente74@gmail.com',

    include_package_data=True,
    packages=[
        'drf_api_dump'
    ],

    url='https://github.com/davidvicenteranz/drf-api-dump/',
    license='MIT license',
    description='Dumps data from apps or models via HTTP',
    long_description=DESCRIPTION,
    install_requires=[
        'djangorestframework'
    ],
    keywords='django dumpdata development',
    classifiers=(
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ),
)