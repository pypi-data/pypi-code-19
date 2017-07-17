# -*- coding:utf-8 -*-
import codecs
from setuptools import setup


with codecs.open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="shadowsocks-py",
    version="2.9.1",
    license='http://www.apache.org/licenses/LICENSE-2.0',
    description="""A fast tunnel proxy that help you get through firewalls,
     the original pypi source is not maintained since version 2.8.2,
     this is a newly maintained pypi source by SilverLining.""",
    author='clowwindy',
    author_email='clowwindy42@gmail.com',
    maintainer='SilverLining',
    maintainer_email='minmin3772@gmail.com',
    url='https://github.com/shadowsocks/shadowsocks',
    packages=['shadowsocks', 'shadowsocks.crypto'],
    package_data={
        'shadowsocks': ['README.rst', 'LICENSE']
    },
    install_requires=[],
    entry_points="""
    [console_scripts]
    sslocal = shadowsocks.local:main
    ssserver = shadowsocks.server:main
    """,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: Proxy Servers',
    ],
    long_description=long_description,
)
