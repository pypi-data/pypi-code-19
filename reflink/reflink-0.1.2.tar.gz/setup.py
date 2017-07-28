#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import sys


from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'cffi',
]

setup_requirements = [
    'cffi',
    'pytest-runner',
]

test_requirements = [
    'pytest',
]

if sys.platform == 'linux' or sys.platform == 'linux2':
    cffi_modules = [
        "reflink/linux.py:ffibuilder"
    ]
elif sys.platform == 'win32':
    cffi_modules = [
        #"reflink/windows.py:ffibuilder"
    ]
else:
    raise NotImplementedError("Platform %s not supported" % sys.platform)

if __name__ == '__main__':
    setup(
        name='reflink',
        version='0.1.2',
        description="Python reflink contai",
        long_description=readme + '\n\n' + history,
        author="Ruben De Smet",
        author_email='pypi@rubdos.be',
        url='https://gitlab.com/rubdos/pyreflink',
        packages=find_packages(include=['reflink']),
        include_package_data=True,
        install_requires=requirements,
        license="MIT license",
        zip_safe=False,
        keywords='reflink',
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
        cffi_modules=cffi_modules,
    )
