"""Unofficial library for Skype API, based on python 3.5+
See:
https://github.com/HolmesInc/PySkype
"""
try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup

setup(
    name='PySkype',
    version='0.0.17',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author="Andrew Babenko",
    author_email="andruonline11@gmail.com",
    description='Unofficial library for Skype API, based on python 3.5+',
    license="LICENSE",
    url='https://github.com/HolmesInc/PySkype',
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)