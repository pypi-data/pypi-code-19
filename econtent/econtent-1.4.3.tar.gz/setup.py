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

setup(
    name = 'econtent',
    packages = ['project'],
    version = '1.4.3',
    description = 'Python module to read extended file content and metadata',
    long_description=long_description,
    author = 'David Betz',
    author_email = 'dfb@davidbetz.net',
    license='MIT',
    url = 'https://github.com/davidbetz/econtent',
    keywords = ['metadata', 'content'],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
)