"""Douban Album Downloader"""

from setuptools import setup, find_packages

requirements = [
    "bs4",
    "requests"
]

setup(
    name="douban-dl",
    version="0.0.1",
    description="douban downloader, include album, celebrity",
    long_description="douban album downloader",
    url="https://github.com/einverne/douban-dl",
    author="einverne",
    author_email="einverne@gmail.com",
    license="MIT",
    # scripts=["bin/douban-album-dl"],
    # not use scripts while use entry_points instead https://packaging.python.org/tutorials/distributing-packages/#scripts
    entry_points={
        'console_scripts': [
            'douban-dl = douban.__main__:main',
        ]},
    keywords="douban downloader",
    packages=find_packages(exclude=["tests"]),
    install_requires=requirements,
)
