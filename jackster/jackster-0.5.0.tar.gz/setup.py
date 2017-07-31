#! /usr/bin/env python3
from setuptools import setup


setup(
    name='jackster',
    packages=['jackster'],
    package_dir={'jackster': 'jackster'},
    license='MIT',
    version='0.5.0',
    description='A micro web framework.',
    author='Daan van der Kallen',
    author_email='mail@daanvdk.com',
    url='https://github.com/daanvdk/jackster',
    download_url='https://github.com/Daanvdk/jackster/archive/0.5.tar.gz',
    keywords=['web', 'framework'],
    classifiers=[],
    install_requires=['werkzeug >= 0.12'],
    test_suite='tests'
)
