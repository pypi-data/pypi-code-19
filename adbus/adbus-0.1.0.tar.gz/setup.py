#!/usr/bin/env python3
# Copyright: 2017, CCX Technologies
"""distutils build and configuration script for python-adbus."""

from distutils.core import setup
from distutils.core import Extension
from Cython.Build import cythonize


def build():
    """Build Package."""

    sdbus = cythonize(
        [Extension("adbus.sdbus", ["adbus/sdbus.pyx"], libraries=["systemd"])]
    )

    setup(
        name='adbus',
        version='0.1.0',
        description='asyncio based dbus interface',
        license='MIT',
        author='CCX Technologies',
        author_email='charles@ccxtechnologies.com',
        url='http://github.com/ccxtechnologies/python-adbus',
        download_url='https://github.com/ccxtechnologies/python-adbus/archive/v0.1.0.tar.gz',
        platforms=['linux'],
        provides=['adbus'],
        packages=['adbus'],
        ext_modules=sdbus
    )


if __name__ == "__main__":
    build()
