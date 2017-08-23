from setuptools import setup, find_packages
from codecs import open
from os import path

import pybittrex

here = path.abspath(path.dirname(__file__))

setup(
    name='PyBittrex',
    version=pybittrex.__version__,
    description='Library for Bittrex API',
    url='https://github.com/mattselph/pybittrex',
    author='Matt Selph',
    author_email='mattselph@outlook.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='bittrex bitcoin ethereum cryptocurrency trading',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['requests']
)
