#!/usr/bin/env python

from setuptools import setup, find_packages

readme = open('README.rst').read()

version = '0.1'

setup(
    name = "blitz-hash",
    version = version,
    packages = ["blitz_hash"],
    author = "Da_Blitz",
    author_email = "code@blitz.works",
    description = "SIMD and coprocessor accelerated hashing functions",
    long_description = readme,
    license = "MIT BSD",
    keywords = "sha sha1 sha256 hashlib hash turbo neon intrinsics simd sse",
    url = "http://blitz.works/blitz-hash",
#    entry_points = {"console_scripts":["epic-server = epicserver.server:main",]},
#    install_requires = ['curio'],
    tests_require = ['pytest', 'mypy', 'hypothesis']
)

