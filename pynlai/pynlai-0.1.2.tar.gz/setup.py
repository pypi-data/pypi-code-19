#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
setup
-----

The pynlai setup script.
'''


from setuptools import setup, find_packages


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY') as history_file:
    history = history_file.read()

requirements = [
    'click',
    'six',
    'spacy',
]

setup_requirements = [
]

test_requirements = [
    'mock',
]

DESCRIPTION = 'PYthon Natural Language Application Interface library.'

LONG_DESCRIPTION = '''
pynlai was created to provide a way for non-technical users to interact
with backend applications using natural language. Developers can simply
write an app and use pynlai to process text commands from any source
(e.g. irc, slack, email, etc.) by decorating their functions with natural
language triggers.

For more information and a guide for getting started, please see our
repo on github linked below.
'''

setup(
    name='pynlai',
    version='0.1.2',
    description="PYthon Natural Language Application Interface library.",
    long_description=LONG_DESCRIPTION + '\n\n' + history,
    author="Chris Pappalardo",
    author_email='cpappalardo@alvarezandmarsal.com',
    url='https://github.com/alvarezandmarsal/pynlai',
    packages=find_packages(include=['pynlai']),
    entry_points={
        'console_scripts': [
            'pynlai=pynlai.cli:entry_point'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='pynlai',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
