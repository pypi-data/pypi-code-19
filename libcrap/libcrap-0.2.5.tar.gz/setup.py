#!/usr/bin/env python

from setuptools import setup


MYPY_VERSION = 'mypy>=0.520'

setup(
    name='libcrap',
    version='0.2.5',
    description='Crappy functions Crabman uses',
    author='Philip Blagoveschensky',
    author_email='me@crabman.me',
    url='https://bitbucket.org/nemelex/libcrap',
    packages=['libcrap'],
    license='MIT',
    install_requires=[
        'tqdm~=4.8.4',
        'typing~=3.5.2.2'],
    extras_require={
        'dev': [
            MYPY_VERSION],
        'test': [
            'pytest~=3.0.4',
            MYPY_VERSION]
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: Software Development :: Libraries :: Python Modules'])
