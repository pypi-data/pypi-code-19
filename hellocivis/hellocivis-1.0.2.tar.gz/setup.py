"""helloworld is a package for testing a CICD pipeline
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    #TODO: these variables should read from a json file
    name='hellocivis',
    version='1.0.2',
    description='A demo of CICD pipeline for Civis Analytics',
    long_description=long_description,
    author='Galen Ballew',
    author_email='galen.ballew@gmail.com',
    url='https://galenballew.github.io/',
    packages=find_packages(exclude=['contrib', 'docs']),
    package_data={'hellocivis': ['scripts/*']},
    entry_points={
        'console_scripts': [
            'hellocivis=hello_civis:main',
        ],
    },
)
