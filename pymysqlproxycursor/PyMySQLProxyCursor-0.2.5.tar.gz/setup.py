#!/usr/bin/env python
from io import open
from setuptools import setup, find_packages

VERSION = "0.2.5"

with open('./README.rst', encoding='utf-8') as file:
    readme = file.read()

REQUIRES = ['PyMYSQL>=0.7.9', 'sqlparse>=0.2.3', 'six>=1.10.0']
setup(
    name="PyMySQLProxyCursor",
    version=VERSION,
    url='https://github.com/DailyHotel/PyMySQLProxyCursor/',
    author='Daily.,Ltd',
    author_email='dev.team@dailyhotel.com',
    maintainer='Randy Yoon',
    maintainer_email='randy.yoon@dailyhotel.com',
    description='Simple PyMySQL ProxyCursor',
    long_description=readme,
    license="MIT",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=REQUIRES,
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Database',
    ],
)
