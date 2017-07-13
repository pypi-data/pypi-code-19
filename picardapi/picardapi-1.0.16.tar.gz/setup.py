from setuptools import setup, find_packages

setup(
    name='picardapi',
    version='1.0.16',
    packages=find_packages(),
    author='picard_username',
    author_email='brig@trialomics.com',
    url='http://picard.io/',
    install_requires=['simplejson>=3.6.5','Unidecode>=0.04.21', 'requests>=2.5.1','ipaddress>=1.0.16','ujson>=1.35', 'Babel>=2.4.0','Faker==0.7.15', 'underscore.py>=0.1.6']
)