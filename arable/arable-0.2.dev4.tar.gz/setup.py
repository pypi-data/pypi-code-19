from setuptools import setup
from arable import __author__
from arable import __version__


setup(
    name='arable',
    packages=['arable'],  # this must be the same as the name above,
    version=__version__,
    description='A client library for connecting with Arable data service',
    author=__author__,
    author_email='developer@arable.com',
    url='https://github.com/Arable/apiclient.git',  # URL github repo
    # download_url='https://github.com/Arable/apiclient.git/tarball/0.1',
    keywords=['weather', 'datascience', 'api'],  # arbitrary keywords
    install_requires=['requests>=2.12.0'],
    classifiers=[],
)
