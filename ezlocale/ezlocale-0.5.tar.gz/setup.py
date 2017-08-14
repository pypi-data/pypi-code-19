from setuptools import setup, find_packages

import ezlocale

with open("readme.rst", "r") as file:
    long_desc = file.read()

setup(
    name='ezlocale',
    description="Easier localization, so everyone can use your programs.",
    long_description=long_desc,
    version=ezlocale.__version__,
    url='https://github.com/reshanie/ezlocale/',
    license='MIT',
    author='Patrick Dill',
    author_email='jamespatrickdill@gmail.com',
    install_requires=["googletrans", "faste"],
    download_url="http://github.com/reshanie/ezlocale/archive/master.tar.gz",

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],

    keywords="translate locale localization translator gettext",

    packages=find_packages(exclude=[".idea"]),
)
