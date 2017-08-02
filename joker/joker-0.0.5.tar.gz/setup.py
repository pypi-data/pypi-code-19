#!/usr/bin/env python3
# coding: utf-8

from setuptools import setup, find_packages


# import joker; exit(1)
# DO NOT import your package from your setup.py


def read(filename):
    with open(filename) as f:
        return f.read()


config = {
    'name': "joker",
    'version': '0.0.5',
    'description': "A virtual package",
    'keywords': 'joker',
    'url': "https://github.com/frozflame/joker",
    'author': 'frozflame',
    'author_email': 'frozflame@outlook.com',
    'license': "GNU General Public License (GPL)",
    'packages': find_packages(),
    'namespace_packages': ["joker"],
    'zip_safe': False,
    'install_requires': read("requirements.txt"),
    'classifiers': [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # ensure copy static file to runtime directory
    'include_package_data': True,
}

setup(**config)
