import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="DriveLink",
    version="0.1.0.1",
    author="Chris Dusold",
    author_email="DriveLink@ChrisDusold.com",
    description=("A set of memory conserving data structures."),
    license=read("LICENSE"),
    keywords="memory",
    url="http://drivelink.rtfd.org/",
    packages=['drivelink', 'tests'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",  # Hopefully.
        "Topic :: Scientific/Engineering",
        "Topic :: Utilities",
    ],
)
