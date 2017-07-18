from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tack',
    version='0.0.0',
    description='Use tackdb instead',
    long_description=long_description,
    author='tackdb'
)
