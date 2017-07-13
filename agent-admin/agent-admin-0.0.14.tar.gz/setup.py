from distutils.core import setup

from setuptools import find_packages

setup(
    name='agent-admin',
    version='0.0.14',
    description='Agent Admin',
    packages=find_packages(exclude=['test', 'test.*', 'docs', 'docs*']),
    license='__license__',
    long_description='Agent Admin',
    install_requires=['libnacl', 'base58', 'requests'],
    scripts=["scripts/run_report", "scripts/manage_config"]
)
