from setuptools import setup, find_packages
from sys import version_info as py_version
from textwrap import dedent

VERSION = '0.0.3'

REQUIREMENTS = ['wrapt>=1.10.8']

setup(
    name='carl',
    version=VERSION,
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    url='https://gitlab.com/tarcisioe/carl',
    download_url=('https://gitlab.com/tarcisioe/carl/repository/'
                  'archive.tar.gz?ref=' + VERSION),
    keywords=['entry', 'points', 'subcommands'],
    maintainer='Tarcísio Eduardo Moreira Crocomo',
    maintainer_email='tarcisio.crocomo+pypi@gmail.com',
    description=(
        'An entry-point library based on argparse, to make creating cli tools '
        'as easy as possible.'
        ),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        ]
)
