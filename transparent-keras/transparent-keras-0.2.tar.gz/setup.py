#!/usr/bin/env python
"""Setup transparent keras"""

from os import path
from setuptools import find_packages, setup


def get_version():
    with open("transparent_keras/__init__.py") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.replace("'", "").replace('"', '').split()[-1]
    raise RuntimeError("Could not find the version string in __init__.py")


NAME = "transparent-keras"
DESCRIPTION = ("Provide a drop-in replacement for a Keras Model that allows a "
               "look under the hood during training")
with open("README.rst") as f:
    LONG_DESCRIPTION = f.read()
MAINTAINER = "Angelos Katharopoulos <katharas@gmail.com>"
MAINTAINER_EMAIL = "katharas@gmail.com"
LICENSE = "MIT"

def setup_package():
    setup(
        name=NAME,
        version=get_version(),
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        license=LICENSE,
        classifiers=[
            "Intended Audience :: Science/Research",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Topic :: Scientific/Engineering",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
        ],
        test_suite="transparent_keras.tests",
        packages=find_packages(exclude=["docs", "tests"]),
        install_requires=["keras>=2"]
    )


if __name__ == "__main__":
    setup_package()
