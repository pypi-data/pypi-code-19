#!/usr/bin/env python3

import os

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'HISTORY.rst')) as f:
    HISTORY = f.read()

requires = []

setup(
    name='mailsave',
    version='0.3.0',
    description='Dump emails to a file. It can be used as a remplacement for sendmail or '
                'an SMTP server.',
    long_description=README + '\n\n' + HISTORY,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Topic :: Communications :: Email',
    ],
    entry_points={
        'console_scripts': [
            'mailsave=mailsave.cli:main'
        ]
    },
    author='Julien Enselme',
    author_email='julien.enselme@centrale-marseille.fr',
    url='https://framagit.org/Jenselme/mailsave',
    keywords='mail',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
)
