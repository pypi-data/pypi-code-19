#!/usr/bin/env python
from setuptools import setup

setup (
    name = 'gwave',
    version = '0.0.1',
    description = 'Meta-package for gravitational-wave data analysis',
    author = 'Ligo Virgo Collaboration',
    author_email = 'alex.nitz@ligo.org',
    url = 'https://ligo-cbc.github.io',
    keywords = ['ligo', 'physics', 'gravity', 'astronomy',
                'gravitational waves', 'data analysis', 'signal processing'],
    install_requires = ['pycbc', 'lal'],
)
