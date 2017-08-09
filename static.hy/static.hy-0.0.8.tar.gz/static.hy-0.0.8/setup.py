#!/usr/bin/env python3

from setuptools import setup

setup(
    name='static.hy',
    version='0.0.8',
    url='https://gitlab.com/robru/static.hy',
    author='Robert Bruce Park',
    author_email='r@robru.ca',
    scripts=['static.hy'],
    license='GNU General Public License version 3',
    description='A static website generator written in Hy.',
    install_requires=['hy', 'markdown', 'jinja2', 'python-dateutil'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Lisp',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Text Processing :: Markup :: HTML',
    ],
)
