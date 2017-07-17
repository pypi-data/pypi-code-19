"""
setup
=====
Setup file for ``runcli``.
"""

from io import open
from setuptools import setup, find_packages
import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


# read in the readme
with open(
        os.path.join(BASE_DIR, 'readme.rst'),
        encoding='utf-8') as readme_file:
    long_description = readme_file.read()

# read in the version
with open(
        os.path.join(BASE_DIR, 'VERSION'),
        encoding='utf-8') as version_file:
    version = version_file.read().strip()


setup(
    name='runcli',
    version=version,
    description='Use Runfiles in your projects.',
    long_description=long_description,
    url='https://github.com/nalourie/runcli',
    author='Nicholas Lourie',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ],
    keywords='development',
    packages=find_packages(),
    install_requires=[],
    extra_require={},
    package_data={},
    data_files=[],
    entry_points={},
    scripts=[
        os.path.join(BASE_DIR, 'bin/run')
    ]
)
