__author__ = 'haibin'

from setuptools import setup

setup(
    name='pycayley',
    version='0.4.0',
    author='zhao haibin',
    author_email='zhaohaibin@outlook.com',
    packages=['pycayley'],
    url='https://github.com/haibin/pycayley',
    license='LICENSE',
    description='Python client for an open-source graph database Cayley',
    install_requires=['requests', 'rdflib'],
    include_package_data=True
)
