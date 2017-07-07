import os
from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/uw-it-aca/uw-restclients-upass>`_.
"""

# The VERSION file is created by travis-ci, based on the tag name
version_path = 'uw_upass/VERSION'
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='UW-RestClients-UPass',
    version=VERSION,
    packages=['uw_upass'],
    author="UW-IT AXDD",
    author_email="aca-it@uw.edu",
    include_package_data=True,
    install_requires=['UW-RestClients-Core>=0.8.9,<1.0',
                      ],
    license='Apache License, Version 2.0',
    description=('A library for connecting to the UPass API'),
    long_description=README,
    url="https://github.com/uw-it-aca/uw-restclients-upass",
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
)
