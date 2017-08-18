#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='mypytex',
    version='0.2',
    description='Writing latex files and compile it with python and jinja2',
    url='https://git.opytex.org/lafrite/Pytex',
    author='Bertrand Benjamin',
    author_email='benjamin.bertrand@opytex.org',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'jinja2',
        'path.py',
        ],
     )

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del

