#!/usr/bin/env python

from setuptools import setup
import os

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

install_requires = [
    'Django>=1.10',
]
version = ('0.4.8')

setup(
    name='webtemplate-dpaw',
    version=version,
    install_requires=install_requires,
    tests_require=install_requires,
    test_suite='runtests.runtests',
    packages=['webtemplate_dpaw'],
    include_package_data=True,
    author='Ashley Felton',
    author_email='asi@dbca.wa.gov.au',
    maintainer='Ashley Felton',
    maintainer_email='asi@dbca.wa.gov.au',
    license='Apache License, Version 2.0',
    url='https://github.com/parksandwildlife/webtemplate',
    description='Base HTML templates for DBCA Django projects',
    long_description=README,
    keywords=['django', 'html', 'template'],
    classifiers=[
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
