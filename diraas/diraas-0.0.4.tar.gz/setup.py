from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()


setup(
    name='diraas',
    version='0.0.4',
    description='Make directory as a service.',
    long_description=long_description,
    author='wonder',
    author_email='wonderbeyond@gmail.com',
    url='',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'Flask~=0.12.2',
    ],
    entry_points={
        'console_scripts': [
            'diraas = diraas.server:main',
        ],
    },
)
