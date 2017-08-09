#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

import gapcheck

setup(
    name='gapcheck',
    version=gapcheck.__version__,
    packages=find_packages(),
    author='penicolas',
    author_email='png1981@gmail.com',
    description='Check gap between tracks',
    long_description="README on github : https://github.com/penicolas/gapcheck",
    install_requires=[
        'sox',
        'mutagen'
    ],
    url='https://github.com/penicolas/gapcheck',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            'gapcheck = gapcheck.gapcheck:main',
        ],
    },
)
