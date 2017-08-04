from setuptools import setup, find_packages

setup(
    name='cumtd-python',
    version='1.0.0',
    packages=find_packages(),
    license='MIT',
    install_requires=['json', 'requests'],
    url='https://github.com/rthotakura97/cumtd-python',
    author='Rohit Thotakura',
    author_email='rthotakura97@gmail.com',
    description='An unnoficial Python client for the CUMTD REST API. '
   )
