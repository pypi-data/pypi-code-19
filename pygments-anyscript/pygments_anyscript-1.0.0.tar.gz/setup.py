#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'pygments',
]

setup_requirements = []

test_requirements = [
    'pytest',
    'pygments'
]

setup(
    name='pygments_anyscript',
    version='1.0.0',
    description="Pygments lexer and style for the AnyScript language",
    long_description=readme + '\n\n' + history,
    author="Morten Enemark Lund",
    author_email='mel@anybodytech.com',
    url='https://github.com/AnyBody/pygments-anyscript',
    packages=find_packages(include=['pygments_anyscript']),
    entry_points={
        'pygments.lexers':
            ['AnyScript = pygments_anyscript:AnyScriptLexer',
             'AnyScriptDoc = pygments_anyscript:AnyScriptDocLexer'],
        'pygments.styles':
            ['AnyScript = pygments_anyscript:AnyScriptStyle']
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords=["pygments", "pygments-anyscript", "lexer",
              "anyscript", "AnyBody Modeling System"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
