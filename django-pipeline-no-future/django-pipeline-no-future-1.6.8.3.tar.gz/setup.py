# -*- coding: utf-8 -*-
import io

from setuptools import setup, find_packages
import sys

install_requires = []

setup(
    name='django-pipeline-no-future',
    version='1.6.8.3',
    description='Pipeline is an asset packaging library for Django.',
    long_description=io.open('README.rst', encoding='utf-8').read() + '\n\n' +
        io.open('HISTORY.rst', encoding='utf-8').read(),
    author='Robin Chew',
    author_email='robin@obsi.com.au',
    url='https://github.com/robinchew/django-pipeline',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.tests']),
    zip_safe=False,
    install_requires=install_requires,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ]
)
