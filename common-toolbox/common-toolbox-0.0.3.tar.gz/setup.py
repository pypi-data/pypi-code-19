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
    version='0.0.3',
    license='MIT',
    description="Common ToolBox",
    install_requires=[
        'pymysql', 'pymongo',
    ],
    packages=find_packages(where='.', exclude=['']),
    test_utils='Test',
    zip_safe=False,
)
