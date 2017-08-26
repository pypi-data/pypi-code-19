#!/usr/bin/env python

from distutils.core import setup

setup(
    name='treespy',
    version='0.1',
    description='Python tree data structures',
    author='bohemian.ai',
    author_email='david.landa@protonmail.ccom',
    url='https://www.github.org/kinotokio/treespy',
    packages=['treespy'],
    extras_require={
        'dev': [
            'pytest'
        ]
    }
)