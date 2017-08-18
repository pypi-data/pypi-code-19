from setuptools import setup
import chanFilter
setup(
    name = "chanFilter",
    version = "0.0.2",
    author = "Jacob Zipper",
    author_email = "zipper@jacobzipper.com",
    description = ("A filtering tool for 4chan to find relevant threads"),
    url = "http://packages.python.org/chanFilter",
    packages=['chanFilter'],
    entry_points={
        "console_scripts": [
            "chanFilter = chanFilter.chanFilter:filter",
        ]
    },
    install_requires=[
        'requests',
        'click'
]
)
