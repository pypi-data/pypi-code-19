import sys

from setuptools import setup, find_packages


PACKAGE_NAME = 'ghlint'
PACKAGE_VERSION = '0.2.2'
MINIMUM_PYTHON_VERSION = '2.7'


def check_python_version():
    """Exit when the Python version is too low."""
    if sys.version < MINIMUM_PYTHON_VERSION:
        sys.exit("Python {0}+ is required.".format(MINIMUM_PYTHON_VERSION))


def build_description():
    """Build a description for the project from the README file."""
    return open("README.rst").read()


check_python_version()

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description='Linting utility for GitHub',
    long_description=build_description(),
    author='Martin Buberl',
    author_email='hello@martinbuberl.com',
    url='https://github.com/martinbuberl/ghlint',
    license='MIT',
    packages=find_packages(exclude=('tests')),
    entry_points={
        'console_scripts': [
            'ghlint=ghlint.cli:main'
        ]
    }
)
