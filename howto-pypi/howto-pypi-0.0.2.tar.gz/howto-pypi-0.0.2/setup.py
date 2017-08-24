from setuptools import setup, find_packages


setup(
    name='howto-pypi',
    version='0.0.2',
    description='A template project about how to package and distribute \
    projects',
    url='https://github.com/yang-zhang/howto-pypi',
    packages=find_packages(exclude=['contrib', 'docs', 'tests'])
)
