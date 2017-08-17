#!/usr/bin/env python

import subprocess

import pip
from setuptools import find_packages
import setuptools.command.build_py as build_py
from setuptools import setup


def _read_requirements(filename):
    reqs_obj = pip.req.parse_requirements(filename,
                                          session=pip.download.PipSession())
    reqs_str = [str(ir.req) for ir in reqs_obj]
    return reqs_str


class BuildReadMeCommand(build_py.build_py):

    def run(self):
        subprocess.run([
            'pandoc',
            '--from', 'markdown',
            '--to', 'rst',
            '--output', 'README.rst',
            'README.md'
        ])


class PersistentPipSyncCommand(build_py.build_py):

    def run(self):
        for filename in ('requirements.txt', 'dev-requirements.txt'):
            subprocess.run(['pip', 'install', '-r', filename])
        for filename in ('requirements.in', 'dev-requirements.in'):
            subprocess.run(['pip-compile', filename])
        subprocess.run([
            'pip-sync',
            'dev-requirements.txt',
            'requirements.txt',
        ])


# https://docs.python.org/3.6/distutils/setupscript.html#additional-meta-data
setup(
    name='bamboo-crawler',
    version='0.0.7',
    description='Hobby Crawler (yet)',
    long_description='''\
bamboo-crawler
============

bamboo-crawler enables continuous growth in crawling task like a bamboo forest.

.. note:: This package is still roughly developing stage.
   So backward compatibility is very fragile at current.
    ''',
    author='Yui Kitsu',
    author_email='kitsuyui+github@kitsuyui.com',
    url='https://github.com/kitsuyui/bamboo-crawler',
    packages=find_packages(),
    install_requires=_read_requirements('requirements.txt'),
    extras_require={
        'dev': _read_requirements('dev-requirements.txt'),
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
    ],
    test_suite='tests',
    tests_require=['nose'],
    scripts=['bamboo_crawler/__main__.py'],
    entry_points={'console_scripts': [
        'bamboo = bamboo_crawler.cli:main',
    ]},
    cmdclass={
        'dev_build_readme': BuildReadMeCommand,
        'dev_persistent_pip_sync': PersistentPipSyncCommand,
    },
    license=open('./LICENSE', 'r').read(),
)
