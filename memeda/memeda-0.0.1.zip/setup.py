#!/usr/bin/env python
# coding:utf-8
#


from setuptools import setup

setup(
    name='memeda',
    version='0.0.1',
    author='physics',
    author_email='jihu9@163.com',
    description='么么哒',
    packages=['memeda'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'memeda=memeda:memeda',
            'dl=memeda:dl'
        ]
    }

)
