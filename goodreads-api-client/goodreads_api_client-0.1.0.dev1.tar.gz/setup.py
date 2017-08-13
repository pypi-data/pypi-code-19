# -*- coding: utf-8 -*-
"""
Goodreads API Client
=====

Goodreads API Client is a non-official Python client for
`Goodreads <http://goodreads.com/>`.
"""
import ast
import re
from setuptools import setup

_version_re = re.compile(r'VERSION\s+=\s+(.*)')

with open('goodreads_api_client/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

tests_require = [
    'pycodestyle==2.3.1',
    'vcrpy==1.11.1',
]

install_requires = [
    'requests==2.18.3',
    'xmltodict==0.11.0',
]

publish_requires = [
    'twine==1.9.1',
    'wheel==0.29.0',
]

extras_require = {
    'publish': publish_requires,
    'test': tests_require,
}

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='goodreads_api_client',
    version=version,
    url='https://github.com/mdzhang/goodreads-api-client-python',
    author='Michelle D. Zhang',
    author_email='zhang.michelle.d@gmail.com',
    description='A non-official client for Goodreads (https://goodreads.com)',
    long_description=readme,
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
    ],
    packages=['goodreads_api_client'],
    extras_require=extras_require,
    tests_require=tests_require,
    install_requires=install_requires,
    test_suite='goodreads_api_client.tests',
    include_package_data=True,
    zip_safe=False,
    platforms=[],
)
