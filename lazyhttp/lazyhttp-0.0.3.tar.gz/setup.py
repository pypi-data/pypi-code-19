#!/usr/bin/env python3
'''
setup.py: Upload to PyPi
'''
import os
from setuptools import setup, find_packages

PKG_NAME = 'lazyhttp'

def contents(*a):
    '''
    Opens a file relative to this file
    '''
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), *a), 'rb') as filedesc:
        return filedesc.read().decode('utf-8')

# Get the version and README
VERSION = contents(PKG_NAME, 'version.py').split()[-1].replace('\'', '')
README = contents('README.md')

setup(
    name=PKG_NAME,
    packages=find_packages(),
    version=VERSION,
    data_files=[('', ['LICENSE']), ],
    entry_points={},
    description='Makes it quick to make HTTP servers',
    long_description=README,
    author='John Andersen',
    author_email='johnandersenpdx@gmail.com',
    url='https://github.com/pdxjohnny/%s' % (PKG_NAME),
    download_url='https://github.com/pdxjohnny/%s/tarball/%s' % (PKG_NAME, VERSION),
    license='MIT',
    keywords=['http', 'server', 'development'],
    classifiers=[
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers'
    ]
)
