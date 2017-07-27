import os
from setuptools import setup

LONG_DESC = open('pypi_readme.rst').read()
LICENSE = open('LICENSE').read()

setup(
    name="yos-cube",
    version="0.0.3",
    description="YOS command line tool for repositories version control, publishing and updating code from remotely hosted repositories, and invoking YOS own build system and export functions, among other operations",
    long_description=LONG_DESC,
    url='https://code.aliyun.com/yos/yos-cube',
    author='YOS',
    author_email='yangsw@mxchip.com',
    license=LICENSE,
    packages=["yos"],
    entry_points={
        'console_scripts': [
            'yos=yos.yos:main',
            'yos-cube=yos.yos:main',
        ]
    },
)
