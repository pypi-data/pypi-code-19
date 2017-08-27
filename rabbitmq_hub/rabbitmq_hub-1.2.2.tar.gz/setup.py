# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

__version__ = '1.2.2'
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name="rabbitmq_hub",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    description="rabbitmq connection manager",
    long_description=README,
    author="Mageia",
    author_email="yzg963@gmail.com",
    zip_safe=False,
    license="Proprietary",
    platforms="any",
    install_requires=['amqp', 'six'],
    entry_points={},
)

