from setuptools import setup, find_packages

setup(
    name="S3ConfigLoader",
    version="0.1.5",
    packages=find_packages(),
    install_requires=['boto3', 'pyyaml'],

    # metadata for upload to PyPI
    author="Rahul Subramaniam",
    author_email="rahulsub@gmail.com    ",
    description="""This package implements a simple config property loader 
    that can read property files from local or from amazon AWS S2""",
    license="PSF",
    keywords="property configuration loader",

    # could also include long_description, download_url, classifiers, etc.
)
