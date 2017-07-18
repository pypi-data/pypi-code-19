# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
long_description = "See website for more info: https://github.com/CTFd/CTFd"

setup(
    name='uctfd',
    version='1.0.3.post1',
    description='Unofficial CTFd split for pypi.',
    long_description=long_description,
    #packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[],
)

