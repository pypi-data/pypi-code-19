import os
import os.path
import re
from setuptools import setup


def get_info(var, pkg):
    """Get version from the package."""
    with open(os.path.join(pkg,'__init__.py')) as f:
        content = f.read()
    return re.search(var + r'\s*=\s*["\'](.+?)["\']', content).group(1)


def get_packages(package):
    """
    Taken from https://github.com/tomchristie/django-rest-framework/blob/master/setup.py
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


NAME = 'popular'
VERSION = get_info('__version__', NAME)
LICENSE = get_info('__license__', NAME)


setup(
    name=NAME,
    description="Minimalist social auth package.",
    url="https://github.com/ryannjohnson/popular-python",
    author="Ryan N Johnson",
    author_email="ryan@ryannjohnson.com",
    license=LICENSE,
    version=VERSION,
    packages=get_packages(NAME),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'requests>=2.14.2',
    ],
)
