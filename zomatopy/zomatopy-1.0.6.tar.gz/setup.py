from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='zomatopy',
    packages=['zomatopy'],
    version='1.0.6',
    url='https://github.com/sharadbhat/Zomatopy',
    description='A simple python wrapper for the Zomato API',
    long_description=long_description,
    author='Sharad Bhat',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='Zomato',
    install_requires=[
        'requests==2.11.1'
    ]
)
