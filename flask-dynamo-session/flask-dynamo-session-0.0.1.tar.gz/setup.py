# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from flask_dynamo_session.__version__ import __version__

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_file = f.read()

setup(
    name='flask-dynamo-session',
    version=__version__,
    description='Flask extension for storing session in dynamodb. Uses flask_dynamo.',
    long_description=readme,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='flask dynamo dynamodb, flask-dynamo',
    author='Austin Page',
    author_email='jaustinpage@gmail.com',
    url='https://github.com/jaustinpage/flask-dynamo-session',
    license=license_file,
    packages=find_packages(exclude=('docs', 'scripts', 'tests')))
