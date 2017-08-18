# encoding: utf-8

from setuptools import setup

setup(
    name="brokerpackager",
    version="0.1.0",
    description="Package Manager based on broker messages",
    author="Big Data",
    author_email="bigdata@corp.globo.com",
    license='MIT',
    include_package_data=True,
    install_requires=[
        "click==6.7",
        "rpy2==2.8.6",
        "stomp.py==4.1.18"
    ],
    packages=['brokerpackager'],
    scripts=["script/broker-packager"]
)
