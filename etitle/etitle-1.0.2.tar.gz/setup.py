from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

try:
   import pypandoc
   long_description = pypandoc.convert('README.md', 'rst')
   with open('README.rst', 'w+') as f:
       f.write(long_description)       
except (IOError, ImportError):
   long_description = ''

from distutils.core import setup
setup(
    name = 'etitle',
    packages = ['etitle'],
    version = '1.0.2',
    description = 'Enables storage and retrieval of extended metadata using filename.',
    long_description=long_description,
    author = 'David Betz',
    author_email = 'dfb@davidbetz.net',
    url = 'https://github.com/davidbetz/pyetitle',
    keywords = ['metadata', 'filename'],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
)
