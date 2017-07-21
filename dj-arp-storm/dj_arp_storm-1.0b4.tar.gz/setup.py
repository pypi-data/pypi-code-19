#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "pyshark",
    "netifaces",
    "pygame",
    "configparser"
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='dj_arp_storm',
    version='1.0b4',
    description="play network traffic as sound",
    long_description=readme + '\n\n' + history,
    author="LISTERINE",
    author_email='jon@jonathanferretti.com',
    url='https://gitlab.com/LISTERINE/dj_arp_storm',
    packages=[
        'dj_arp_storm',
    ],
    package_dir={'dj_arp_storm':
                 'dj_arp_storm'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='dj_arp_storm',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points = {
        'console_scripts': ['dj_as=dj_arp_storm.command_line:main'],
    }
)
