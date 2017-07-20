from setuptools import setup, find_packages
import os

name = 'densenlpt'
version = '0.0.1'

try:
    with open('README.rst') as f:
        readme = f.read()
except IOError:
    readme = ''

def read_from_file(filename):
    return open(filename).read().splitlines()


short_description = '`densenlpt` is a package for creating dictionary and vector from scentences & training model to predict.'


setup(
    name=name,
    version=version,
    url='https://github.com/k-mawa/densenlpt',
    description=short_description,
    long_description=readme,
    keywords=['nlp','gensim','machine','machine learning','scikit-learn','sklearn','mecab','natto'],
    packages=find_packages(),
    install_requires=read_from_file('requirements.txt'),
    author='Kosuke Mawatari',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: MIT License',
    ],

)