#!/usr/bin/env python3
import os
import re
import setuptools


here = os.path.abspath(os.path.dirname(__file__))


def get_meta():
    with open(os.path.join(here, 'owattr.py')) as f:
        source = f.read()

    regex = r'^{}\s*=\s*[\'"]([^\'"]*)[\'"]'
    return lambda name: re.search(
        regex.format(name), source, re.MULTILINE).group(1)


meta = get_meta()

with open(os.path.join(here, 'README.rst')) as f:
    readme = f.read()

install_requires = []

test_requires = [
    'Pygments',
    'docutils',
    'flake8',
    'mypy',
    'pytest',
    'pytest-cov',
]

setuptools.setup(
    name='owattr',
    version=meta('__version__'),
    description="owattr overwrites attributes.",
    long_description=readme,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries"
    ],
    keywords=["attrs", "overwrite"],
    author=meta('__author__'),
    author_email=meta('__email__'),
    url="https://github.com/narusemotoki/owattr",
    license=meta('__license__'),
    py_modules=['owattr'],
    install_requires=install_requires,
    extras_require={
        'test': test_requires,
    },
    include_package_data=True,
)
