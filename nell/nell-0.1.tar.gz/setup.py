# coding=utf-8
# Copyright 2016 Flowdas Inc. <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from setuptools import setup, find_packages

setup_requires = [
    'setuptools>=35.0',
]

install_requires = [
]

tests_require = [
    'pytest>=3.1',
    'coverage>=4.4',
    'tox>=2.7',
]

dependency_links = [
]

ext_modules = [
]

setup(
    name='nell',
    version=open('VERSION').read().strip(),
    url='https://bitbucket.org/flowdas/nell',
    description='Nell: A mostly static site generator',
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
            'nell=nell.base:main',
        ],
    },
    zip_safe=False,
    keywords=('website', 'blog', 'static'),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Utilities',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Text Processing :: Markup',
    ],
)
