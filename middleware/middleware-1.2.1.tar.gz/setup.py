from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README'), encoding='utf-8') as f:
    long_description = f.read()

from distutils.core import setup
setup(
    name = 'middleware',
    packages = ['project'],
    version = '1.2.1',
    description = 'Python module to add general middleware',
    long_description=long_description,
    author = 'David Betz',
    author_email = 'dfb@davidbetz.net',
    url = 'https://github.com/davidbetz/middleware',
    keywords = ['middleware'],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
)
