#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 's5s',
    version = '0.0.1',
    keywords = ('shadowsocks', 'socks5'),
    description = 'a simple socks5 server',
    license = 'MIT License',

    url = 'https://www.jiguang.cn',
    author = 'c161216',
    author_email = 'c161216@gmail.com',

    packages = ['s5s'],
    package_data={
        's5s': ['README.rst']
    },    
    include_package_data = True,
    platforms = 'any',
    install_requires = ['shadowsocks'],
        entry_points="""
    [console_scripts]
    s5ss = s5s.s5s:main
    """,
)
