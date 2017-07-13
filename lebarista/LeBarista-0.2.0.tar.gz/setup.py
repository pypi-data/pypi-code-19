from distutils.core import setup

setup(
    # Application name:
    name="LeBarista",
    version="0.2.0",

    # Application author details:
    author="Tnarik Innael",
    author_email="tnarik@lecafeautomatique.co.uk",


    url="https://github.com/tnarik/lebarista",

    # Modules
    py_modules=["lebarista"],

    # Packages
    #packages=["lebarista"],

    # Include additional files into the package
    include_package_data=True,

    #
    # license="LICENSE.txt",
    description="A notifications tool.",

    # long_description=open("README.txt").read(),

    keywords = ['slack', 'notifications'],

    # Dependent packages (distributions)
    install_requires=[
        "slackclient",
        "PyYAML"
    ],
)