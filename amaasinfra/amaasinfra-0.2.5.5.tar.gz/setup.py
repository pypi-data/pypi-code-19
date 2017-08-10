from setuptools import setup, find_packages

setup(
    name='amaasinfra',
    keywords=['amaas', 'infra', 'aws'],
    description='This is an essential package for managing AMaaS infra layer',
    license='Apache License 2.0',
    install_requires=['boto3', 'troposphere','pymysql'],
    version='0.2.5.5',
    author='AMaaS Pte Ltd',
    author_email='tech@amaas.com',
    packages=find_packages(),
    platforms='any',
)
