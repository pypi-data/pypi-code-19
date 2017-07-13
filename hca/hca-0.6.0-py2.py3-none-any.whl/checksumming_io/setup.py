#!/usr/bin/env python

import glob
from setuptools import setup, find_packages

setup(
    name="checksumming_io",
    version="0.0.1",
    url='https://github.com/HumanCellAtlas/checksumming_io',
    license='Apache Software License',
    author='Human Cell Atlas contributors',
    author_email='spierson@chanzuckerberg.com',
    description='IO buffers that generate checksums',
    long_description=open('README.rst').read(),
    install_requires=[
        'crcmod==1.7'
    ],
    extras_require={
        ':python_version == "3.6"': ['enum34 >= 1.1.6, < 2']
    },
    packages=find_packages(exclude=['tests']),
    scripts=glob.glob('scripts/*'),
    platforms=['MacOS X', 'Posix'],
    # package_data={'hcacli': ['*.json']},
    zip_safe=False,
    include_package_data=True,
    test_suite='tests',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        # 'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
