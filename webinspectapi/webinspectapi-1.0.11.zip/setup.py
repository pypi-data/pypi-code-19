#!/usr/bin/env python

import os
import sys

from webinspectapi import __version__ as version

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst', 'r') as f:
    readme = f.read()

# Publish helper
if sys.argv[-1] == 'build':
    os.system('python setup.py sdist bdist_wheel')
    sys.exit(0)

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel upload -r pypi')
    sys.exit(0)
    
if sys.argv[-1] == 'tag':
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit(0)

if sys.argv[-1] == 'publish-test':
    os.system('python setup.py sdist bdist_wheel upload -r pypitest')
    sys.exit(0)

setup(
    name='webinspectapi',
    packages=['webinspectapi'],
    version=version,
    description='A Python module to assist with the WebInspect RESTFul API to administer scans.',
    long_description=readme,
    author='Brandon Spruth, Jim Nelson',
    author_email='brandon.spruth2@target.com, jim.nelson2@target.com',
    url='https://github.com/target/webinspectapi',
    download_url='https://github.com/target/webinspectapi/tarball/' + version,
    license='MIT',
    install_requires=['requests'],
    keywords=['webinspect', 'api', 'security', 'software', 'hpe', 'micro focus'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.0',
    ]
)
