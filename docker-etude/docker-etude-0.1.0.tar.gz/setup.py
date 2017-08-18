#!/usr/bin/env python
from setuptools import find_packages, setup

project = "docker-etude"
version = "0.1.0"

setup(
    name=project,
    version=version,
    description="Build Docker Compositions, Especially For Local Development",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/docker-etude",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    keywords="docker",
    install_requires=[
        "boto3>=1.4.6",
        "click>=6.7",
        "PyYAML>=3.12",
    ],
    setup_requires=[
        "nose>=1.3.7",
    ],
    dependency_links=[
    ],
    entry_points={
        "console_scripts": [
            "etude = docker_etude.main:etude",
        ],
    },
    tests_require=[
        "coverage>=4.4.1",
        "mock>=2.0.0",
        "PyHamcrest>=1.9.0",
    ],
)
