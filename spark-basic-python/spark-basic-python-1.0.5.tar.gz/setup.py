#!/usr/bin/env python
# coding: utf-8

from setuptools import setup
from setuptools import find_packages

PACKAGE = "spark_basic_python"
NAME = "spark-basic-python"
DESCRIPTION = "pyspark_develop"
AUTHOR = "yaoboxu_18333"
AUTHOR_EMAIL = "18333@etransfar.com"
URL = "http://10.7.15.220:8090/display/sonar/Pyspark"
VERSION = __import__(PACKAGE).__version__

# curr_dir = os.path.dirname(os.path.realpath(__file__))
# config_file = {'prop1': curr_dir + '\\..\\resources\\pg.datasource.ini',
#                'prop2': curr_dir + '\\..\\resources\\sparkbasic.ini'}
# print curr_dir + '\\..\\resources\\pg.datasource.ini'
# print curr_dir + '\\..\\resources\\sparkbasic.ini'
# print os.path

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open('README.rst').read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="BSD",
    url=URL,
    packages=find_packages(exclude=["tests.*", "tests"]),
    # package_data={'': ['*.rst'],
    #               'spark_basic_python': 'resources/*.ini'},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
    include_package_data=True
)
