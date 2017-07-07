#!/usr/bin/env python

from distutils.core import setup
# you can also import from setuptools

setup(
    name='zabbixactivechecks',
    packages=['zabbixactivechecks'],
    version='0.0.3',

    description='Implementation of Zabbix Agent Active checks protocol',
    long_description=(
        'This module implements Zabbix Active Checks Protocol.\n'
        'It allows fetching of active checks for given host'
        ' from Zabbix server\n'
        'Based on the work by:\n'
        'Matt Parr @ https://github.com/MattParr\n'
    ),
    author='Alen Komic',
    author_email='akomic@gmail.com',
    license='GPL',
    url='https://github.com/akomic/zabbix-activechecks',
    download_url='https://github.com/akomic/zabbix-activechecks',
    keywords=['monitoring', 'zabbix', 'trappers'],
    classifiers=[],
)
