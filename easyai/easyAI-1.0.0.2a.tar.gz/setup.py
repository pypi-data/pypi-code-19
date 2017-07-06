#!/usr/bin/env python

from distutils.core import setup
setup(
    name='easyAI',
    url='https://github.com/Zulko/easyAI',
    version='1.0.0.2a',
    description='Easy-to-use game AI algorithms (Negamax etc.)',
    long_description=open('README.rst').read(),
    license='MIT',
    keywords="board games AI artificial intelligence negamax",
    packages=['easyAI'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License"
    ]
)
