#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'nltk',
    'numpy',
]

test_requirements = [
]

setup(
    name='clds_pipeline',
    version='0.1.4',
    description="Cross Language Document Similarity Pipeline for Master's Thesis",
    long_description=readme + '\n\n' + history,
    author="Nate Guerin",
    author_email='nathan.guerin@gmail.com',
    url='https://github.com/gusennan/clds_pipeline',
    packages=[
        'clds_pipeline',
    ],
    package_dir={'clds_pipeline':
                 'clds_pipeline'},
    entry_points={
        'console_scripts': [
            'clds_pipeline=clds_pipeline.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='clds_pipeline',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
