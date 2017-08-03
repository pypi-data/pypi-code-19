#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io

from setuptools import setup

with io.open('README.rst', encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0'
]

test_requirements = [
    'nose==1.3.7'
]

setup(
    name='distill.py',
    version='0.0.2',
    description="Doc platform for coder.",
    long_description=readme + '\n\n' + history,
    author="Vu Anh",
    author_email='brother.rain.1024@gmail.com',
    url='https://github.com/magizbox/distill.py',
    packages=[
        'distill',
    ],
    package_dir={'distill': 'distill'},
    entry_points={
        'console_scripts': [
            'distill=distill.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='underthesea',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
