import os
import unittest

from setuptools import setup, find_packages


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as fp:
        return fp.read()

def test_suite():
    test_loader = unittest.TestLoader()
    return test_loader.discover('tests', pattern='test_*.py')


setup(
    name='ebird-import',
    version='0.3.0',
    description='Tools for loading records into eBird',
    long_description=read("README.rst"),
    author='Stuart MacKay',
    author_email='smackay@flagstonesoftware.com',
    url='http://pypi.python.org/pypi/ebird-import/',
    license='GPL',
    packages=find_packages(),
    scripts=['bin/ebird-convert'],
    keywords='eBird import csv',
    test_suite='setup.test_suite',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Natural Language :: English",
        "Topic :: Text Processing :: Filters",
    ],
    install_requires=[
        'pycli',
    ],
)
