#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os.path as P
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

current_dir = P.dirname(__file__)
with open(P.join(current_dir, "pyliveleak/VERSION")) as fin:
    version = fin.read().strip()

requirements = [
    'Click>=6.0',
    'lxml',
    'requests<3.0.0',
    'requests-toolbelt',
    'PyYAML'
]

setup_requirements = [
    'pytest-runner',
    # TODO(mpenkov): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    'mock',
    # TODO: put package test requirements here
]

setup(
    name='pyliveleak',
    version=version,
    description="Uploads videos to liveleak.com",
    long_description=readme + '\n\n' + history,
    author="Michael Penkov",
    author_email='misha.penkov@gmail.com',
    url='https://github.com/mpenkov/pyliveleak',
    packages=find_packages(include=['pyliveleak']),
    entry_points={
        'console_scripts': [
            'pyliveleak=pyliveleak.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords=['pyliveleak', 'liveleak'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    download_url='https://github.com/mpenkov/pyliveleak/archive/0.1.1.tar.gz',
    package_data={'pyliveleak': ['categories.yml', 'VERSION']}
)
