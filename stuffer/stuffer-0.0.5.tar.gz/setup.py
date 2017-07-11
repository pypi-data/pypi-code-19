#! /usr/bin/env python3
import sys
from pathlib import Path

from setuptools import setup, find_packages


readme_note = """\
.. note:: For the latest source, please visit the
   `Bitbucket repository <https://bitbucket.org/mapflat/stuffer>`_
   

"""

long_description = readme_note + Path(sys.argv[0]).with_name('README.rst').read_text()

setup(
    name="stuffer",
    description = 'Simplified, container-friendly provisioning',
    long_description = long_description,
    maintainer="Lars Albertsson",
    maintainer_email="lalle@mapflat.com",
    url="http://bitbucket.org/mapflat/stuffer",
    version='0.0.5',
    packages=find_packages(exclude=["tests"]),
    entry_points="""
      [console_scripts]
      stuffer=stuffer.main:cli
    """,
    install_requires=['click']
)
