#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version():
    return '0.1.1'


version = get_version()

readme = open('README.rst').read()

setup(
    name='django_api_view',
    version=version,
    description="""Django api view""",
    long_description=readme,
    author='Anthon Alindada',
    author_email='anthon.alindada.435@gmail.com',
    url='https://github.com/anthon-alindada/django_api_view',
    packages=[
        'django_api_view',
    ],
    include_package_data=True,
    install_requires=[
        'Django>=1.8',
    ],
    license="MIT",
    zip_safe=False,
    keywords='django api view',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
