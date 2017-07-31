# Adapted from https://github.com/pypa/sampleproject/blob/master/setup.py
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))


def read(filename):
    with open(filename, 'r') as f:
        return f.read()


# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='studentit-bookit-client',
    version='0.1.0',
    description='API client and command line application for connecting to BookIT',
    long_description=long_description,
    # The project's main homepage.
    url='https://github.com/cmbrad/studentit-bookit-client',
    # Author details
    author='Christopher Bradley',
    author_email='chris.bradley@unimelb.edu.au',
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(include=['studentit*']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=read('runtime-requirements.txt').split('\n'),
    entry_points={
        'console_scripts': [
            'bookit=bookit.cli:main',
        ],
    },
)
