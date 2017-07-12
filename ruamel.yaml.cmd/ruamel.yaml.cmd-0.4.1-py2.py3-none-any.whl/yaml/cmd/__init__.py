# coding: utf-8

from __future__ import print_function, absolute_import, division, unicode_literals

_package_data = dict(
    full_package_name='ruamel.yaml.cmd',
    version_info=(0, 4, 1),
    __version__='0.4.1',
    author='Anthon van der Neut',
    author_email='a.van.der.neut@ruamel.eu',
    description='commandline utility to manipulate YAML files',
    entry_points='yaml',
    since=2015,
    nested=True,
    install_requires=[
        'ruamel.std.argparse>=0.8',
        'configobj',
        'ruamel.yaml.convert>=0.3',
    ],
    extras_require={
        'configobj': ['configobj']
    },
    universal=True,
    tox=dict(
        env='23',
    ),
)

version_info = _package_data['version_info']
__version__ = _package_data['__version__']
