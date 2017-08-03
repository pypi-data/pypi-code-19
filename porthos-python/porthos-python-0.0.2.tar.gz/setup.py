#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='porthos-python',
    version='0.0.2',
    author='Germano Fronza',
    author_email='germano.inf@gmail.com',
    maintainer='Germano Fronza',
    maintainer_email='germano.inf@gmail.com',
    packages=['porthos', 'porthos.client'],
    install_requires=['pika>=0.11.0b1'],
    url='https://github.com/porthos-rpc/porthos-python',
    bugtrack_url='https://github.com/porthos-rpc/porthos-python/issues',
    license='BSD',
    description='A RPC over AMQP library for python',
    keywords='python, rpc, amqp, rpc-client',
    platforms='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Topic :: Utilities',
    ],
)
