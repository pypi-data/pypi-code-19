#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import dirname, abspath, join

from pip.download import PipSession
from pip.req import parse_requirements
from setuptools import setup, find_packages


def get_path(*p):
    return join(dirname(abspath(__file__)), *p)


install_reqs = parse_requirements(get_path('requirements.txt'), session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]


setup(
    name="python-faasclient",
    url="https://github.com/globocom/python-faasclient",
    version='0.3.2',
    description='Python mock to the Filer as a Service API.',
    author='Mauro Murari',
    author_email='mauro_murari@hotmail.com',
    packages=find_packages(),
    install_requires=reqs,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'faas = bin.commands:cli',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    zip_safe=False,
)
