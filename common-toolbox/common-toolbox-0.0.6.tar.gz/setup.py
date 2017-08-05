#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 下午2:49
# @Author  : Hou Rong
# @Site    : 
# @File    : setup.py.py
# @Software: PyCharm
from setuptools import setup, find_packages

setup(
    name='common-toolbox',
    version='0.0.6',
    license='MIT',
    description="A python toolbox contains several function you might need",
    author='Henry Hou',
    author_email='nmghr9@gmail.com',
    url='https://github.com/nmghr9/CommonToolBox',
    install_requires=[
        'scipy',
        'pymysql',
        'pymongo',
        'pillow',
        'nose'
    ],
    packages=find_packages(where='.', exclude=['']),
    test_utils='Test',
    zip_safe=False,
)
