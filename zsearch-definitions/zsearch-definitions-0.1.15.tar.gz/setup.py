from setuptools import setup, find_packages

setup(
    name = "zsearch-definitions",
    description = "Egg version of files that can be used for interacting with zdb through python",
    version = "0.1.15",
    license = "Apache License, Version 2.0",
    author = "Censys Team",
    author_email = "team@censys.io",
    maintainer = "Censys Team",
    maintainer_email = "team@censys.io",
    keywords = "python json zsearch",
    zip_safe = False,
    install_requires = [
        "grpcio==1.2.1",
        "protobuf==3.2.0",
    ],
    packages = [
        "zsearch_definitions",
    ]
)
