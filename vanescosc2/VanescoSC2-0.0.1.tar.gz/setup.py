#!/usr/bin/env python
from setuptools import setup

setup(
    name='VanescoSC2',
    version='0.0.1',
    description='StarCraft II AI',
    author='TheChyz',
    author_email='cmichal@hotmail.ca',
    license='MIT',
    url='https://github.com/TheChyz/VanescoSC2',
    packages=[
        'VanescoSC2',
    ],
    install_requires=[
        's2clientprotocol>=1.0',
        'websocket-client',
    ],
)
