#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import re
import os
import sys

name = 'gb-openapi-codec'

def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


version = get_version('gb_openapi_codec')

TWINE_USERNAME = os.environ.get('TWINE_USERNAME')
TWINE_PASSWORD = os.environ.get('TWINE_PASSWORD')


if sys.argv[-1] == 'publish':
    if os.system("pip freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python setup.py sdist")
    os.system("twine upload -u '{}' -p '{}' dist/{}-{}.tar.gz".format(
        TWINE_USERNAME, TWINE_PASSWORD, name, version))
    print("You probably want to also tag the version now:")
    print("  git tag -a {0} -m 'version {0}'".format(version))
    print("  git push --tags")
    sys.exit()


setup(
    name=name,
    version=version,
    url='http://github.com/crowdcomms/gb-openapi-codec/',
    license='BSD',
    description='An OpenAPI codec for Core API.',
    author='Adam Jacquier-Parr',
    author_email='ajparr@crowdcomms.com.au',
    packages=get_packages('gb_openapi_codec'),
    package_data=get_package_data('gb_openapi_codec'),
    install_requires=['coreapi>=2.2.0'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    # entry_points={
    #     'coreapi.codecs': [
    #         'openapi=openapi_codec:OpenAPICodec'
    #     ]
    # }
)
