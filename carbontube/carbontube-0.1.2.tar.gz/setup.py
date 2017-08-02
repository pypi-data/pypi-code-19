#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import os
from setuptools import setup, find_packages


local_file = lambda *f: \
    open(os.path.join(os.path.dirname(__file__), *f), 'rb').read()


class VersionFinder(ast.NodeVisitor):
    VARIABLE_NAME = 'version'

    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        try:
            if node.targets[0].id == self.VARIABLE_NAME:
                self.version = node.value.s
        except:
            pass


def read_version():
    finder = VersionFinder()
    finder.visit(ast.parse(local_file('carbontube', 'version.py')))
    return finder.version


dependencies = filter(bool, map(bytes.strip, local_file('requirements.txt').splitlines()))

setup(
    name='carbontube',
    version=read_version(),
    description="\n".join([
        'CarbonTube is a ZeroMQ-based distributed pipeline framework.',
    ]),
    entry_points={
        'console_scripts': ['carbontube = carbontube.console.main:entrypoint'],
    },
    author='Gabriel Falcao',
    author_email='gabriel@nacaolivre.org',
    url='https://github.com/gabrielfalcao/carbontube',
    packages=find_packages(exclude=['*tests*']),
    install_requires=dependencies,
    include_package_data=True,
    package_data={
        'carbontube': 'COPYING *.rst docs/* carbontube/storage/redis-lua-scripts/* carbontube/storage/* docs/source/* requirements.txt carbontube/web carbontube/web/* carbontube/web/dist carbontube/web/dist/* carbontube/web/templates carbontube/web/templates/*'.split(),
    },
    zip_safe=False,
)
