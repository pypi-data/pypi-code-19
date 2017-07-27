#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages

requirements = [
    'click',
    'boto3'
]

setup(
    name="firehoser",
    version='1.0.3',
    description='Command line tool that automates the setup of a lambda function that fowards records from Kinesis to Firehose.',
    url='https://github.com/bufferapp/firehoser',
    author='David Gasquez',
    author_email='davidgasquez@buffer.com',
    license='MIT',
    keywords='kinesis aws firehose lambda',
    py_modules=['firehoser'],
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'firehoser=firehoser.cli:firehoser'
        ]
    }
)
