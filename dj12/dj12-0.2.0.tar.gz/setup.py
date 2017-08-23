#!/usr/bin/env python3

from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name = 'dj12',
    version = '0.2.0',
    description = "12factor config support for Django",
    long_description = readme,
    author = "Aiakos Contributors",
    author_email = "aiakos@aiakosauth.com",
    url = "https://gitlab.com/aiakos/dj12",
    keywords = "django 12factor configuration",

    install_requires = [
        'django',
        'dj-database-url',
        'dj-email-url',
        'django-cache-url',
        'six',
    ],

    packages = ['dj12'],
    zip_safe = True,

    license = "MIT",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
