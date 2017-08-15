#!/usr/bin/env python
from setuptools import setup, find_packages

with open('README.md') as buff:
    longdes = buff.read()

with open('changelog.md') as buff:
    longdes += buff.read()

CLASSIFIERS = [
    'Programming Language :: Python :: 3',
    'Topic :: Utilities',
    'Topic :: Education',
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    'Development Status :: 5 - Production/Stable'
]

setup(
    name='essential-pathway',
    version='1.0',
    keywords=['ep','epw','environment variables','path','pathway','essential pathway'],
    description='Manage your most commonly used directories in command line, requires the tcl edition Environment Module.',
    long_description=longdes,
    author='realasking',
    author_email='realasking@gmail.com,tomwangsim@163.com',
    url='https://github.com/realasking/essential-pathway',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['prettytable'],
    scripts=['bin/ep'],
    platforms=['linux','cygwin','freebsd','Unix'],
    classifiers=CLASSIFIERS,
)
