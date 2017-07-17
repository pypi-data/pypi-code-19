from setuptools import setup, find_packages
import os
import sys


setup(
    name="ioant",
    version="0.3.5",
    packages=find_packages(),
    include_package_data=True,
    author="Adam Saxen",
    author_email="adam@asaxen.com",
    description="This is the official IOAnt package. Contains the SDK, Proto-generator and utils",
    license="MIT",
    keywords="",
    url="http://ioant.com",   # project home page, if any
    install_requires=[
        "nose>=1.3.7",
        "mock>=2.0.0",
        "paho-mqtt>=1.2",
        "protobuf>=3.0.0"
    ],

)
