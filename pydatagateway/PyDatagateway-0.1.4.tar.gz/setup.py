#!/usr/bin/env python

from setuptools import setup
import pydatagateway
import sys

setup(
    name="PyDatagateway",
    version=pydatagateway.__version__,
    description="Python interface to Datagateway",
    url='https://github.com/yanyu-singapore/PyDatagateway.git',
    author="Yanyu Qu",
    author_email="yanyuqu@gmail.com",
    license="Apache License, Version 2.0",
    packages=['pydatagateway', 'TCLIService'],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Database :: Front-Ends",
    ],
    install_requires=[
        'future',
    ],
    extras_require={
        "Presto": ['requests>=1.0.0'],
        "Hive": ['sasl>=0.2.1', 'thrift>=0.10.0', 'thrift_sasl>=0.1.0'],
        "SQLAlchemy": ['sqlalchemy>=0.5.0'],
    },
    tests_require=[
        'mock>=1.0.0',
        'pytest',
        'pytest-cov',
        'requests>=1.0.0',
        'sasl>=0.2.1',
        'sqlalchemy>=0.5.0',
        'thrift>=0.8.0',
    ],
    package_data={
        '': ['*.rst'],
    },
    entry_points={
        # New versions
        'sqlalchemy.dialects': [
            'hive = pydatagateway.sqlalchemy_hive:HiveDialect',
            'presto = pydatagateway.sqlalchemy_presto:PrestoDialect',
        ],
        # Version 0.5
        'sqlalchemy.databases': [
            'hive = pydatagateway.sqlalchemy_hive:HiveDialect',
            'presto = pydatagateway.sqlalchemy_presto:PrestoDialect',
        ],
    }
)
