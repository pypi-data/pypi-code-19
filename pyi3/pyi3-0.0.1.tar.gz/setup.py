from setuptools import setup, find_packages
from sys import version_info as py_version

VERSION = '0.0.1'

VERSION_REQUIREMENTS = []
MODULES = []

if py_version < (3, 5):
    MODULES.append('subprocess35')
    VERSION_REQUIREMENTS.append('typing')

setup(
    name='pyi3',
    version=VERSION,
    url='https://gitlab.com/tarcisioe/pyi3',
    download_url=('https://gitlab.com/tarcisioe/carl/repository/'
                  'archive.tar.gz?ref=' + VERSION),
    keywords=['i3', 'type'],
    maintainer='Tarcísio Eduardo Moreira Crocomo',
    maintainer_email='tarcisio.crocomo+pypi@gmail.com',
    description='A type-hinted python module to communicate with i3.',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    install_requires=VERSION_REQUIREMENTS,
    py_modules=MODULES,
)
