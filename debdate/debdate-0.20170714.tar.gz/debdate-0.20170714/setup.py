#!/usr/bin/env python3

from setuptools import setup

setup(
    name='debdate',
    version='0.20170714',
    scripts=['debdate'],
    install_requires=[
        'python-dateutil',
        ],
    author="Elena ``of Valhalla'' Grandi",
    author_email="valhalla@trueelena.org",
    description='Convert Gregorian dates to Debian Regnal dates',
    url='http://git.trueelena.org/cgit.cgi/software/debdate/about/',
    license='WTFPLv2',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: DFSG approved',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Religion',
        'Topic :: Utilities',
        ]
)
