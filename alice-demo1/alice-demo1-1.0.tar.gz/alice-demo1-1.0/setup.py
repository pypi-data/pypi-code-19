'''
Setup stable.world

'''

from setuptools import find_packages, setup

setup(
    name='alice-demo1',
    version='1.0',
    author="Alice",
    author_email="srossross@gmail.com",
    description="Alice open source package",
    license="BSD",
    packages=find_packages(),
    install_requires=[
        'certifi',
    ],
)
