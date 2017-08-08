#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as readme_file, open('HISTORY.rst') as history_file:
    long_description = (readme_file.read() + "\n\n" + history_file.read())

requirements = [
    'click>=6.0',
    'jinja2',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='qchviewer',
    version='0.1.3',
    description="A simple script to directly open standalone Qt Help file by Assistant",
    long_description=long_description,
    author="Hong-She Liang",
    author_email='starofrainnight@gmail.com',
    url='https://github.com/starofrainnight/qchviewer',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'qchviewer=qchviewer.__main__:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License",
    zip_safe=False,
    keywords='qchviewer',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
