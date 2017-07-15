from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'econtent',
    packages = ['project'],
    version = '1.4.1',
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