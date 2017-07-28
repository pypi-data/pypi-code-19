#!/usr/bin/env python
# coding: utf-8

from setuptools import setup
from setuptools import find_packages

#setup(
#    name='spark-basic-python',
#    version='0.0.1',
#    author='yaoboxu_18333',
#    author_email='18333@etransfar.com',
#    url='http://10.7.15.220:8090/display/sonar/Pyspark',
#    description='pyspark_develop',
#    packages=['python'],
#    install_requires=[],
#    entry_points={
#        'console_scripts': []
#    }
#)

PACKAGE = "spark_basic_python"
NAME = "spark-basic-python"
DESCRIPTION = "pyspark_develop"
AUTHOR = "yaoboxu_18333"
AUTHOR_EMAIL = "18333@etransfar.com"
URL = "http://10.7.15.220:8090/display/sonar/Pyspark"
VERSION = __import__(PACKAGE).__version__

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
    package_data={'': ['*.rst']},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
    zip_safe=False,
)