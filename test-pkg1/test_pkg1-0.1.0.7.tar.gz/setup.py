#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import versioneer
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    # TODO: put package requirements here
]

setup_requirements = [
    # TODO(limitlessv): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='test_pkg1',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Testing cookiecutter",
    long_description=readme + '\n\n' + history,
    author="Shmuel Maruani",
    author_email='shmuel@limitlessv.com',
    url='https://github.com/limitlessv/test_pkg1',
    packages=find_packages(include=['test_pkg1']),
    entry_points={
        'console_scripts': [
            'test_pkg1=test_pkg1.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='test_pkg1',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
