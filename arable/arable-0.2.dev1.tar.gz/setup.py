from setuptools import setup

setup(
    name='arable',
    packages=['arable'],  # this must be the same as the name above,
    version='0.2.dev1',
    description='A client library for connecting with Arable data service',
    author='Arable Labs, Inc',
    author_email='developer@arable.com',
    url='https://github.com/Arable/apiclient.git',  # URL github repo
    download_url='https://github.com/Arable/apiclient.git/tarball/0.1',
    keywords=['weather', 'datascience', 'api'],  # arbitrary keywords
    install_requires=['requests>=2.12.0'],
    classifiers=[],
)
