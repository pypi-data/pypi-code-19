import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "python-cip",
    version = "0.0.4",
    author = "Fabio Comuni",
    author_email = "f.comuni@creative-group.it",
    description = ("Very simple python interface to Canto Cumulus CIP"),
    license = "LGPLv2+",
    keywords = "network",
    url = "https://bitbucket.org/fcomuni/python_cip",
    packages=['cip'],
    install_requires=['requests>=2.12'],
    python_requires='>=2.7, <4',

    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
    ],
)
