import os
from os.path import exists
from setuptools import setup, find_packages

import tahoma_api

setup(
    name='tahoma_api',
    version=tahoma_api.__version__,
    url='http://github.com/philklei/tahoma-api/',
    license='Apache Software License',
    author='Philip Kleimeyer',
    install_requires=[],
    author_email='philip.kleimeyer@gmail.com',
    description='Tahoma Api - Python connect to Tahoma REST API',
    long_description=open('README.rst').read() if exists("README.rst") else "",
    packages=['tahoma_api'],
    include_package_data=True,
    keywords='tahoma somfy io covers senors api',
    platforms='any'
)