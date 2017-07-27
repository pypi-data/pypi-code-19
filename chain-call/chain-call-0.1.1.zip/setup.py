from setuptools import setup, find_packages
from os import path

setup(
    name = "chain-call",
    version = "0.1.1",
    description = "Call a function with a chain",
    long_description = "Call a function with a chain",
    author = "Yixian Du",
    license = "MIT",
    classifiers = [
      'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',  
    ],
    keywords = "chain",
    packages = find_packages(),
    install_requires=[],
     entry_points={
        'console_scripts': [
            'chain=chain:main',
        ],
    },
)