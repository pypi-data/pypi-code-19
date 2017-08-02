from setuptools import setup
import os

setup(
    name='segment_source',
    packages=['segment_source'],
    version='0.10.1',
    description='Python source client',
    author='Segment',
    author_email='friends@segment.com',
    url='https://github.com/segmentio/python-source',
    install_requires=[
        'grpcio==1.0.0'
    ]
)
