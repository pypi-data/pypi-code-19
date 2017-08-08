# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('reactjo/reactjo.py').read(),
    re.M
    ).group(1)


with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name = "reactjo",
    packages = ["reactjo"],
    entry_points = {
        "console_scripts": ['reactjo = reactjo.reactjo:main']
        },
    version = 1.3,
    description = "Extensible scaffolding engine.",
    long_description = long_descr,
    author = "Aaron Price",
    author_email = "coding.aaronp@gmail.com",
    url = "https://github.com/aaron-price/reactjo.git"
    )
