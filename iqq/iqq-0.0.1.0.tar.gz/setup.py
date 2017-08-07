#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = 'iqq',
    version = '0.0.1.0',
    packages = find_packages(),
    install_requires=[
        'qqbot',
    ],

    entry_points={
        'console_scripts': [
            'iqq = src:login',
        ],
    },

    license = 'Apache License',
    author = 'muduo',
    author_email = 'imuduo@163.com',
    url = '',
    description = 'qq智能客服',
    keywords = ['qq', '智能客服'],
)
