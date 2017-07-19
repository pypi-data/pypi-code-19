#!/usr/bin/env python
import os, sys
from setuptools import setup, Command,find_packages
import qcloudcli


def main():
    setup(
        maintainer_email="szyqstu@gmail.com",
        name='qcloudcli',
        description='Universal Command Line Environment for qcloud',
        version='1.8.2',
        url='http://www.qcloud.com/',
        packages = find_packages(),
        platforms=['unix', 'linux', 'win64'],
		#install_requires = install_requires,
        author='cj',
        author_email='xxx',
		scripts = ['qcloudcli/shellcomplete.sh'],
        py_modules=['qcloudcli'],
        entry_points = {
            'console_scripts': [
                'qcloudcli = qcloudcli.Qcloudcli:main',
                'qcloud_completer  = qcloudcli.completer:complete',
            ]
        }
        
    )


if __name__ == '__main__':
    main()
