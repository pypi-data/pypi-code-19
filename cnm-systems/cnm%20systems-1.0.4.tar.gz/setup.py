# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.txt'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="cnm systems",
    version="1.0.4",
    author="Andrew Carnegie",
    author_email="mrhieutrieu@gmail.com",
    description=("System of Cinnamon"),
    license="BSD",
    keywords="development",
    url="https://github.com/hieutrieu/systems",
	packages=['cnm_systems', 'cnm_systems/services','cnm_systems/migrations'],
    long_description=long_description,
	install_requires=['emails', 'django-ckeditor'],
    classifiers=[
		"License :: OSI Approved :: MIT License",
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
    ],	
)