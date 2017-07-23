from distutils.core import setup
from setuptools import find_packages
setup(
    name = 'krikos',
    packages=find_packages(exclude=['examples']),
    data_files=[(['krikos'])],
    install_requires=['numpy'],
    version = '0.1',
    description = 'Python ML library for experimentation with neural networks',
    author = 'Shubhang Desai',
    author_email = 'shubhang@stanford.edu',
    url = 'https://github.com/shubhangdesai/krikos',
    download_url = 'https://github.com/shubhangdesai/krikos/archive/0.1.tar.gz',
    keywords = ['machine-learning', 'neural-networks', 'artificial-intelligence', 'ml', 'nn', 'ai'],
    classifiers = [],
)