#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from setuptools import setup


setup(
    name='ytsearch',
    version='0.2.2dev',
    description='A program to search and diplay youtube videos.',
    author='Steven J. Core',
    license='GPL3.0',
    packages=['ytsearch', 'ytsearch.ui'],
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'youtube-dl',
        'urwid',
        'requests',
        'pyyaml',
        'pafy',
        'clipboard',
        'fuzzywuzzy',
        'python-Levenshtein'
        ],
    entry_points={
        'console_scripts': [
            'ytsearch = ytsearch.program:main',
            ]
        })
