# libsne, a Python library for SNE synchronous exchanges
# Copyright (C) 2017 Cliss XXI
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# coding: utf-8 
#!/usr/bin/env python
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def get_version(*file_paths):
    """Retrieves the version from the given file path."""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

try:
    import pypandoc
    readme = pypandoc.convert('README.md', 'rst')
    changelog = pypandoc.convert('CHANGELOG.md', 'rst')
except ImportError:
    if 'sdist' in sys.argv or 'bdist_wheel' in sys.argv:
        raise RuntimeError("You must install 'pypandoc' at first.")
    print("Warning! You will have to install 'pypandoc' if you want to "
          "build the package and upload it on PyPi.")
    readme = open('README.md').read()
    changelog = open('CHANGELOG.md').read()

version = get_version('libsne', '__init__.py')

setup(
    name='libsne',
    version=version,
    description='Python library for SNE synchronous exchanges',
    long_description=readme,
    url='http://trac.interne.cliss21.org/libsne/',
    author='Cliss XXI',
    author_email='contact@cliss21.org',
    packages=['libsne'],
    include_package_data=True,
    install_requires=['jinja2', 'lxml', 'six'],
    license="GNU AGPL-3",
    zip_safe=False,
    keywords='libsne',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: French',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
