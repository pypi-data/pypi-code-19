from setuptools import setup

url = "https://github.com/JIC-CSB/dtool-create"
version = "0.1.0"
readme = open('README.rst').read()

setup(
    name="dtool-create",
    packages=["dtool_create"],
    version=version,
    description="Dtool plugin for creating datasets and collections",
    long_description=readme,
    include_package_data=True,
    author="Tjelvar Olsson",
    author_email="tjelvar.olsson@jic.ac.uk",
    url=url,
    install_requires=[
        "Click",
        "dtoolcore",
        "dtool_cli",
        "ruamel.yaml",
    ],
    entry_points={
        "dtool.dataset": [
            "create=dtool_create.dataset:create",
            "readme=dtool_create.dataset:readme",
            "freeze=dtool_create.dataset:freeze",
        ],
    },
    download_url="{}/tarball/{}".format(url, version),
    license="MIT"
)
