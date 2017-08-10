#!/usr/bin/env python
"""This module uses setuptools to facilitate building & installing"""

from setuptools import setup

setup(
    name='hoottit',
    version='0.1.dev0',
    packages=['hoottit'],
    author='Robert Badea',
    author_email='owlree128@gmail.com',
    description='Simple tool that caches Reddit submissions and comments',
    license=open('LICENSE').read(),
    url='https://github.com/Owlree/hoottit',
    long_description=open('README.txt').read(),
    entry_points={
        'console_scripts': [
            'hoottit = hoottit.__main__:main'
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha'
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License'
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP'
    ],
)
