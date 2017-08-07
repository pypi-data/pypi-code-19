import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "kolla-ansible-plugins",
    version = "0.0.0",
    author = "Duong Ha-Quang",
    author_email = "duonghq@vn.fujitsu.com",
    description = ("Provide plugins for openstack/kolla-ansible"),
    license = "GPLv3",
    keywords = "kolla-ansible",
    url = "http://packages.python.org/kolla-ansible-plugins",
    packages=['kolla_ansible_plugins'],
    long_description=read('README'),
    classifiers=[
        "Environment :: OpenStack",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5"
    ],
)
