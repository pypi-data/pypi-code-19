#!/usr/bin/env python3

from setuptools import setup

setup(
    name = "hclib",
    py_modules = ["hclib"],
    version = "0.1.12",
    description = "A library to connect to https://hack.chat/",
    long_description = open("./info.rst").read(),
    url = "https://github.com/neelkamath/hack.chat-library",
    author = "Neel Kamath",
    author_email = "neelkamath@protonmail.com",
    license = "MIT",
    keywords = "hack.chat library",
    install_requires = ["websocket-client"]
)
