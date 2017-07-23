#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup

classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3 :: Only",
    "Topic :: Multimedia",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Image Recognition",
    "Topic :: Utilities"
]

requires = [
    'argparse',
    'numpy',
    'scikit-image',
    'six',
    'sklearn'
]

setup(
    name='classify_image_dimension',
    version='0.0.1',
    description='classify images by dimension',
    author='Yassu',
    author_email='mathyassu@gmail.com',
    url='https://github.com/yassu/ClassifyImageDimension',
    classifiers=classifiers,
    packages=['classify_image_dimension'],
    install_requires=requires,
    entry_points="""
       [console_scripts]
       classify_image_dimension = \
           classify_image_dimension.classify_image_dimension:main
    """
)
