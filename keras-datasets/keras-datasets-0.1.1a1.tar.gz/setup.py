#!/usr/bin/env python
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

# To use a consistent encoding
from codecs import open

from keras_datasets import __version__

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='keras-datasets',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=__version__,

    description='A package to download common deep learning and machine datasets, convert them in hdf5 format in order to be in your Keras graph with a queue runner',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/DEKHTIARJonathan/keras-datasets',
    download_url='https://github.com/DEKHTIARJonathan/keras-datasets/archive/master.zip',

    # Author details
    author='Jonathan DEKHTIAR, Marc MOREAUX',
    author_email='contact@jonathandekhtiar.eu, mr.moreaux@gmail.com',

    # maintainer Details
    maintainer='Jonathan DEKHTIAR, Marc MOREAUX',
    maintainer_email='contact@jonathandekhtiar.eu, mr.moreaux@gmail.com',

    # The licence under which the project is released
    license='MIT',

    classifiers=[
        # How mature is this project? Common values are
        #  1 - Planning
        #  2 - Pre-Alpha
        #  3 - Alpha
        #  4 - Beta
        #  5 - Production/Stable
        #  6 - Mature
        #  7 - Inactive
        'Development Status :: 1 - Planning',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',

        # Indicate what your project relates to
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

        # Additionnal Settings
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: OS Independent',
    ],
    keywords='keras dataset deeplearning library machinelearning datascience python python3 python2',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'future==0.16.0',
        'numpy==1.13.1',
        'scipy==0.19.1',
        'Pillow==4.2.1',
        'tensorflow==1.3.0',
        'Theano==0.9.0',
        'Keras==2.0.6',
    ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,travis]
    extras_require={
        'dev': [
            'twine',
            'check-manifest',
            'coverage'
        ],
        'travis': [
            'coverage',
            'coveralls'
        ]
    },

    zip_safe=True,
)
