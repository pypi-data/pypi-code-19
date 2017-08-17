#!/usr/bin/env python
import os
try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup

from keras_datasets import __version__

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    long_description = readme.read()

setup(
    name='keras_datasets',
    version=__version__,
    packages=['keras_datasets',],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=long_description,
)
'''
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from keras_datasets import __version__

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    long_description = readme.read()

setup(name='keras_datasets',
    version=__version__,
    description='Python 2 and 3 interface to download Keras Datasets',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 ',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English',
    ],
    keywords='keras datasets deeplearning machinelearning datascience python python3 python2',
    author='Jonathan DEKHTIAR',
    author_email='contact@jonathandekhtiar.eu',
    maintainer='Jonathan Dekhtiar',
    maintainer_email='contact@jonathandekhtiar.eu',
    url='https://github.com/DEKHTIARJonathan/keras_datasets',
    license='GPLv3',
    packages=['keras_datasets'],
    install_requires=[],
    zip_safe=False,
    test_suite='nose.collector',
    tests_require=['nose'],
)
'''
