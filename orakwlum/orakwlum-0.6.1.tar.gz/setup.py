# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

INSTALL_REQUIRES = ['m3-cdecimal', 'enerdata', 'delorean', 'pymongo', 'redis', 'rq', 'one_year_ago', 'pandas', 'numpy']

setup(
    name='orakwlum',
    description='oraKWlum lib',
    version='0.6.1',
    url = 'https://github.com/gisce/orakWlum',
    download_url = 'https://github.com/gisce/orakWlum/archive/v0.6.0.tar.gz',
    author='GISCE Enginyeria, SL',
    author_email='devel@gisce.net',
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    license='General Public Licence 3',
    provides=['orakwlum'],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5"
    ]
)

