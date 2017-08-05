#!/usr/bin/env python

import pip
from setuptools import find_packages
from setuptools import setup


def _read_requirements(filename):
    reqs_obj = pip.req.parse_requirements(filename,
                                          session=pip.download.PipSession())
    reqs_str = [str(ir.req) for ir in reqs_obj]
    return reqs_str


setup(
    name='bamboo-crawler',
    version='0.0.5',
    description='Hobby Crawler (yet)',
    author='Yui Kitsu',
    author_email='kitsuyui+github@kitsuyui.com',
    url='https://github.com/kitsuyui/bamboo-crawler',
    packages=find_packages(),
    install_requires=_read_requirements('requirements.txt'),
    extras_require={
        'dev': _read_requirements('dev-requirements.txt'),
    },
    scripts=['bamboo_crawler/__main__.py'],
    entry_points={'console_scripts': [
        'bamboo = bamboo_crawler.cli:main',
    ]},
)
