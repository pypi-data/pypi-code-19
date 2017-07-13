# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="booley",
    version="0.1.2",
    author="Alberto Casero",
    author_email="kas.appeal@gmail.com",
    packages=["booley"],
    url="https://github.com/kasappeal/booley",
    license="MIT",
    description="A meta-language to evaluate boolean expressions using a dict keys as context variables.",
    install_requires=["pyparsing"],
)
