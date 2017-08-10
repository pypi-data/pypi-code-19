# -*- coding: utf-8 -*-
#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='pyOneLine',
    version='1.1.24',
    description='I wish we can solve all questions with one-line code!',
    url='https://github.com/StephenZMZ/OneLine.git',
    author='Stephen.Z',
    author_email='15242200221@163.com',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='python one line',
    packages = find_packages(exclude = ['MANIFEST.in']),
    include_packages_data = True
    )   
