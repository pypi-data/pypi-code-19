#! /usr/bin/env python3

from setuptools import setup, find_packages


setup(
    name="stuffer",
    maintainer="Lars Albertsson",
    maintainer_email="lalle@mapflat.com",
    url="http://bitbucket.org/mapflat/stuffer",
    version='0.0.4',
    packages=find_packages(exclude=["tests"]),
    entry_points="""
      [console_scripts]
      stuffer=stuffer.main:cli
    """,
    install_requires=['click']
)
