#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os, sys
from setuptools import setup, find_packages

if sys.argv[-1] == 'publish':
    #os.system('python setup.py register')
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload --universal')
    sys.exit()

version = '0.0.3'
requirements = [
    'Click>=6.0',
    'python-gantt==0.6.0',
    'python-dateutil==2.6.1'
]

def read(f):
    return open(f, encoding='utf-8').read()

setup(
    name='clitheroe',
    version='0.0.3',
    description="Sprint plan gant chart generator.",
    long_description="Because someone always wants a gant chart.",
    author="Ben Hughes",
    author_email='bwghughes@gmail.com',
    url='https://github.com/bwghughes/clitheroe',
    py_modules=['clitheroe'],
    entry_points={
        'console_scripts': [
            'clitheroe=clitheroe:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='clitheroe, gant',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
)
