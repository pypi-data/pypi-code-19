#!/usr/bin/env python
from setuptools import setup, find_packages

__version__ = 1.41

setup(
    name='nexusmaker',
    version=__version__,
    description="nexusmaker - Nexus file maker for language phylogenies",
    url='',
    author='Simon J. Greenhill',
    author_email='simon@simon.net.nz',
    license='BSD',
    zip_safe=True,
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='language-phylogenies',
    packages=find_packages(),
    install_requires=['python-nexus', ],
    setup_requires=['pytest-runner', ],
    tests_require=['pytest', ],
)
