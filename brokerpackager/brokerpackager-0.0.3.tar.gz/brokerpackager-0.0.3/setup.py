# encoding: utf-8

from setuptools import setup, find_packages

setup(
    name="brokerpackager",
    version="0.0.3",
    description="Package Manager based on broker messages",
    author="Big Data",
    author_email="bigdata@corp.globo.com",
    license='MIT',
    install_requires=[
        "click==6.7",
        "rpy2==2.8.6",
        "stomp.py==4.1.18"
    ],
    packages=find_packages(),
    scripts=["script/broker-packager"]
)
