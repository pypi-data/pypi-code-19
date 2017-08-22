from distutils.core import setup
from setuptools import find_packages

from keyman import __version__

import sys
print(sys.getdefaultencoding())

setup(
    name="keyman",
    version=__version__,

    author="psrit",
    author_email="xiaojx13@outlook.com",
    url="",

    description="A simple command-line password manager.",
    long_description=open("README.rst").read(),

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        # "Natural Language :: Chinese (Simplified)",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Topic :: Database",
    ],

    packages=find_packages(),

    entry_points={
        "console_scripts": [
            "keyman = keyman.__main__:main",
        ],
    },

    install_requires=["pycrypto"],
)
