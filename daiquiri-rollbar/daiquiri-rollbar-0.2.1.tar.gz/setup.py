#!/usr/bin/env python3

import os

from setuptools import (
    find_packages,
    setup,
)


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGELOG.rst')) as f:
    CHANGELOG = f.read()

with open('requires.txt', 'r') as requires:
    install_requires = requires.read().split('\n')

setup(
    name='daiquiri-rollbar',
    version='0.2.1',
    description='Easy way to integrate Rollbar into daiquiri',
    long_description=README + '\n\n' + CHANGELOG,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: System :: Logging',
    ],
    author='Julien Enselme',
    author_email='jenselme@jujens.eu',
    url='https://gitlab.com/Jenselme/daiquiri-rollbar',
    keywords='daiquiri logging rollbar',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
)
