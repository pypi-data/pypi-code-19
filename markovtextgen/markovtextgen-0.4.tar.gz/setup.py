
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='markovtextgen',
    version='0.4',
    description='Simple module for text generation with a Markov model',
    url='https://github.com/bonnieetc/markov-text',
    author='Bonnie Lampard',
    author_email='bonnie.lampard@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='ngram markov generator nlp',
    py_modules=["markovtextgen"],
    install_requires=[ 'numpy'],

   
)
