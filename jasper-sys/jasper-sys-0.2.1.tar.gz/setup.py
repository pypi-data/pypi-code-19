#!/usr/bin/env python3

from setuptools import setup
from os import path

HERE = path.abspath(path.dirname(__file__))

try:
    with open(path.join(HERE, 'README.md')) as f:
        description = f.read()
except:
    description = ''

setup(
    name='jasper-sys',
    version='0.2.1',
    description='JASPER SYS',
    long_description=description,
    url='https://github.com/fabiocody/jasper.git',
    author='Fabio Codiglioni',
    author_email='fabiocody@icloud.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 4 - Beta'
    ],
    keywords='jasper, system, process monitor',
    py_modules=['jaspercore', 'jasperctl'],
    install_requires=['psutil', 'bottle', 'requests'],
	entry_points={
        'console_scripts': [
            'jasperctl=jasperctl:main',
        ],
    }
)
