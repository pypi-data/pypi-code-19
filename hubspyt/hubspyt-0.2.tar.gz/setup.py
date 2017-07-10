from setuptools import setup

setup(
    name='hubspyt',
    packages=['hubspyt', 'hubspyt.models'],
    version='0.2',
    description='HubSpot API Wrapper',
    author='Jeff Allen',
    author_email='jeff.allen127@gmail.com',
    url='https://github.com/MailValet/hubspyt',
    download_url='https://github.com/MailValet/hubspyt/archive/master.zip',
    install_requires=['requests'],
)
