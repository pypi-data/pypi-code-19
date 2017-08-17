#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast

from setuptools import setup, find_packages


def get_version():
    with open('sqreen/__init__.py') as fileobj:
        for line in fileobj:
            if line.startswith('__version__ ='):
                return ast.literal_eval(line.split('=', 1)[1].strip())


long_description = """Sqreen is a SaaS based Application protection and monitoring platform that integrates directly into your Python applications.
Learn more at `<https://www.sqreen.io/>`_."""


setup(
    name='sqreen',
    version=get_version(),
    description="Sqreen agent to protect Python applications.",
    long_description=long_description,
    author="Boris Feld",
    author_email='boris@sqreen.io',
    url='https://www.sqreen.io/',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_dir={'sqreen':
                 'sqreen'},
    package_data={'sqreen': ['*.crt']},
    include_package_data=True,
    install_requires=['py-mini-racer>=0.1.10'],
    license="Copyright",
    zip_safe=False,
    keywords='sqreen',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=[],
    entry_points={
        'console_scripts': [
            "sqreen-start = sqreen.bin.protect:protect"
        ]
    }
)
