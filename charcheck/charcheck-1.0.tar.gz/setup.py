from setuptools import setup

setup(
    name='charcheck',
    packages = ["charcheck"],
    entry_points = {
        "console_scripts": ['charcheck = charcheck.charcheck:main']
    },
    version = 1.0,
    description = "Command line tool to compare translated files",
    author = "Abhishek Roul",
    author_email = "asmuth444@gmail.compile",
    install_requires = ['xmltodict'],
    url = "https://github.com/asmuth444/charcheck"

)