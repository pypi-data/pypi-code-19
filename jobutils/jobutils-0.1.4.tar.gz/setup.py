from setuptools import setup

setup(
    name='jobutils',
    version='0.1.4',
    author='joberate',
    packages=['DataAccess', 'DataMining', 'LocationClients', 'Utils'],
    include_package_data=True,
    description='Helpers for data related activities',
    long_description=open('README.md').read(),
    install_requires=["pandas ", "numpy", 'Pillow', 'dpath', 'nltk', 'networkx', 'pymongo', 'py2neo', 'pika']
)