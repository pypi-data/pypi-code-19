#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os.path import join, dirname
from io import open


setup(
    name='pandas-charm',
    version='0.1.3',
    description=(
        'A small Python library for getting character matrices '
        '(alignments) into and out of pandas'),
    long_description=open(
        join(dirname(__file__), 'README.rst'), encoding='utf-8').read(),
    packages=find_packages(exclude=['docs', 'tests*']),
    py_modules=['pandascharm'],
    install_requires=['pandas>=0.16', 'numpy'],
    extras_require={'testing': [
        'coverage', 'pytest', 'biopython', 'dendropy']},
    author='Markus Englund',
    author_email='jan.markus.englund@gmail.com',
    url='https://github.com/jmenglund/pandas-charm',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=['alignment', 'BioPython', 'DendroPy', 'pandas'],
)
