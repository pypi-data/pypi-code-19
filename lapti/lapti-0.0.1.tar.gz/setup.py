# -*- coding: utf-8 -*-
import codecs
from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
with codecs.open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [x.strip() for x in f.readlines()]

setup(
    name='lapti',
    version='0.0.1',
    description='Simple utils for flask and peewee projects',
    author='VonZeleny',
    author_email='ivanzeleny@ya.ru',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='peewee flask utils',
    data_files=[
        ('', ['requirements.txt', 'README.rst', ], ),
    ],
    packages=find_packages(include=['lapti']),
    install_requires=requirements
)
