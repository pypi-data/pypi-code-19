#!/usr/bin/env python
"""setup file for mimir cli"""
from setuptools import setup, find_packages
from mimir_cli.main import __version__
PROJECT = 'mimir-cli'
VERSION = __version__
setup(
    name=PROJECT,
    version=VERSION,
    description='mimir cli application',
    long_description='mimir cli application',
    author='Jacobi Petrucciani',
    author_email='jacobi@mimirhq.com',
    url='',
    download_url='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
        'Environment :: Console',
    ],
    platforms=['Any'],
    scripts=[],
    provides=[],
    install_requires=[
        'cliff>=2.0.0',
        'requests>=2.10.0',
        'requests[security]'
    ],
    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'mimir = mimir_cli.main:main'
        ],
        'mimir_cli.cli': [
            'complete = mimir_cli.main:Complete',
            'version = mimir_cli.main:Version',
            'submit = mimir_cli.main:Submit',
            'login = mimir_cli.main:Login',
            'logout = mimir_cli.main:Logout',
        ],
    },
    zip_safe=False,
)
