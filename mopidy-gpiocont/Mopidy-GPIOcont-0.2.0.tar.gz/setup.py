from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    with open(filename) as fh:
        metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", fh.read()))
        return metadata['version']


setup(
    name='Mopidy-GPIOcont',
    version=get_version('mopidy_gpiocont/__init__.py'),
    url='https://github.com/jaspergerth/mopidy-gpiocont',
    license='Apache License, Version 2.0',
    author='Jasper Gerth',
    author_email='jaspergerth@gmail.com',
    description='Extension to control musicbox via gpio.',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 1.0',
        'Pykka >= 1.1',
        'smbus >= 1.1',
    ],
    entry_points={
        'mopidy.ext': [
            'gpiocont = mopidy_gpiocont:Extension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
