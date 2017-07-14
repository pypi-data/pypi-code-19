import os
import re
from setuptools import setup

def version():
    regex = r'^(?m){}[\s]*=[\s]*(?P<ver>\d*)$'

    with open(os.path.join(os.path.dirname(__file__), 'include.mk')) as f:
        ver = f.read()

    major = re.search(regex.format('MAJORVERSION'), ver).group('ver')
    minor = re.search(regex.format('MINORVERSION'), ver).group('ver')
    patch = re.search(regex.format('PATCHLEVEL'), ver).group('ver')
    return "{}.{}.{}".format(major, minor, patch)

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='parsing-tools',
    version=version(),
    packages=['mimeparser', 'xml2dict',],
    include_package_data=True,
    license='MIT License',
    description=('A set of utilities to help parse mime types found in '
                 'HTTP headers plus a utility to parse XML documents into '
                 'Python objects.'),
    long_description=README,
    url='https://github.com/cnobile2012/parsing_tools/',
    author='Carl J. Nobile',
    author_email='carl.nobile@gmail.com',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        ],
    install_requires=[
        'defusedxml',
        'six',
        ],
    )
