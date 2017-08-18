#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

setup(
    name='flask-automation',
    # When changing this version number, remember to update CHANGELOG.
    version='1.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Common functionality across the different Flask microservices of the UofC UIS Automation team',
    long_description=open('README.rst').read(),
    url='https://git.csx.cam.ac.uk/i/ucs/automation/flask-automation',
    author='Automation team, University Information Services, University of Cambridge',
    author_email='automation@uis.cam.ac.uk',
    install_requires=[
        'flask'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
