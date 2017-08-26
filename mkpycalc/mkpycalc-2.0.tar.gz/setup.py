import os
from distutils.core import setup

from setuptools import find_packages

root_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root_dir, "VERSION")) as f:
    VERSION = f.read().rstrip()

setup(
    name='mkpycalc',

    version=VERSION,

    install_requires=[
        'mklibpy'
    ],

    packages=find_packages(),

    entry_points={
        'console_scripts': [
            'pycalc=mkpycalc:run_from_command_line',
        ],
    },

    url='https://github.com/MichaelKim0407/PyCalculator',

    license='MIT',

    author='Michael Kim',

    author_email='mkim0407@gmail.com',

    description='',

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",

        "Topic :: Software Development :: Libraries",
        "Topic :: Terminals",
        "Topic :: Utilities",
    ]
)
