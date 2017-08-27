# coding=utf-8
# Copyright 2017 Flowdas Inc. <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from setuptools import setup, find_packages

with open('VERSION') as f:
    VERSION = f.read().strip()

setup_requires = [
    'setuptools>=35.0',
]

install_requires = [
    'flowdas-meta>=1.0.1,<1.1',
    'click>=6.7,<6.8',
    'PyYAML>=3.12,<3.13',
]

tests_require = [
    'pytest>=3.1,<3.2',
    'coverage>=4.4,<4.5',
    'tox>=2.7,<2.8',
    'pytest-xdist',
]

dependency_links = [
]

ext_modules = [
]

setup(
    name='launch',
    version=VERSION,
    url='https://bitbucket.org/flowdas/launch',
    description='Launch: An Application Launcher',
    author='Flowdas Inc.',
    author_email='prospero@flowdas.com',
    license='MPL 2.0',
    packages=find_packages(exclude=['tests']),
    ext_modules=ext_modules,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    dependency_links=dependency_links,
    scripts=[],
    entry_points={
        'console_scripts': [
            'launch=launch.cli:main',
        ],
    },
    zip_safe=False,
    keywords=('cli', 'configuration', 'plugin'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
