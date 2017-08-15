import codecs
import os
from setuptools import setup, find_packages


PACKAGE = "kyroller"
VERSION = __import__(PACKAGE).__version__

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname), 'r', 'utf-8').read()


setup(
    name="kyroller",
    version=VERSION,
    author="ShangHai Shilai",
    author_email="developers@kuaiyutech.com",
    description='''快雨量化框架''',
    license="BSD",
    keywords="stock kuaiyutech",
    url="http://packages.python.org/kyroller",
    packages=find_packages(exclude=["tests.*", "tests"]),
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)
