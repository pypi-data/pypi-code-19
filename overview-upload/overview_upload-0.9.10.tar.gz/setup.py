#!/usr/bin/env python3

import os
from setuptools import setup

def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding="utf-8") as f:
        return f.read()

setup(
    name='overview_upload',
    version='0.9.10',
    description='Upload documents to Overview web server',
    long_description=read_file('README.rst'),
    url='https://github.com/overview/overview-upload-directory',
    install_requires=[
        'requests>=2.17.3',
        'rfc6266>=0.0.4',
    ],
    packages=[ 'overview_upload' ],
    scripts=[ 'overview-create-document-set', 'overview-upload', 'overview-upload-csv' ],
    classifiers=(
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    )
)
