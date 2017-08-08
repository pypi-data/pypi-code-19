#!/usr/bin/env python
# programmer : Daofeng

from setuptools import setup


setup (
    name='submitTaRGET',
    version='1.0.0',
    description='Bulk upload data to target dcc',
    url='https://github.com/xzhuo/TargetBulkUpload',
    author='Xiaoyu Zhuo',
    license='MIT',
    python_requires='>=3',
    install_requires=['xlrd'],
    entry_points={
        'console_scripts': [
            'submitTaRGET=submitTaRGET:main',
        ],
    },
)
