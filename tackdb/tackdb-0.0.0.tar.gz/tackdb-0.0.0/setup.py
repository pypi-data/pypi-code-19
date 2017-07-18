from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
    name='tackdb',
    version='0.0.0',
    description='tackdb python driver',
    long_description=long_description,
    author='mtso'
)
