#! /usr/bin/python
# coding: utf-8

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'doc/README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='getmagpi',
    version='0.2.1',
    description='A simple utility to synchronize free MagPi PDF content.',
    long_description=long_description,
    url='https://jnario.github.io/getmagpi/',
    author='Jose Nario',
    author_email='jose@nario.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: System :: Archiving :: Mirroring',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='magpi raspberrypi library',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['requests'],

    entry_points={
        'console_scripts': [
            'getmagpi = src.getmagpi:main',
        ],
    },
)
