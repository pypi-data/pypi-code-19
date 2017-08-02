#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup

setup(
    name='recopytex',
    version='0.1',
    description='Tools to manipulate scores',
    url='https://git.opytex.org/lafrite/Recopytex',
    author='Bertrand Benjamin',
    author_email='benjamin.bertrand@opytex.org',
    license='MIT',
    packages=['Recopytex'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_restplus',
        'flask_sqlalchemy',
    ],
)

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del

