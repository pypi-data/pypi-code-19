#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()

requirements = [
    'click>=6.0',
    'jinja2',
]

setup(
    name='jinja2-pimport',
    version='0.1.6',
    author='Hong-She Liang',
    author_email='starofrainnight@gmail.com',
    maintainer='Hong-She Liang',
    maintainer_email='starofrainnight@gmail.com',
    license='MIT',
    url='https://github.com/starofrainnight/jinja2-pimport',
    description='Jinja2 Extension for Python Import',
    long_description=read('README.rst'),
    packages=[
        'jinja2_pimport',
    ],
    package_dir={'jinja2_pimport': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python',
    ],
    keywords=['jinja2', 'extension', 'import'],
)
