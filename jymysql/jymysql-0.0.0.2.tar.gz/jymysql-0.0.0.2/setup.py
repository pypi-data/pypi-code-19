#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='jymysql',
    version='0.0.0.2',
    description=(
        '对mysql操作的orm'
    ),
    long_description=open('README.rst').read(),
    author='Jython',
    author_email='ijython@qq.com',
    maintainer='Jython',
    maintainer_email='ijython@qq.com',
    license='BSD License',
    packages=find_packages(),
    platforms=[
        "all"],
    url='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        #'MySQL-python>=1.2.3',
    ]
)
