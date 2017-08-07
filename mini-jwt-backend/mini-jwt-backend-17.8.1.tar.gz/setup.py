import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='mini-jwt-backend',
    version='17.8.1',
    packages=find_packages(),
    install_requires=[
        'djangorestframework',
        'djangorestframework-jwt',
        'requests'
    ],
    include_package_data=True,
    license='MIT',
    description='A simple JWT Django Auth backend',
    long_description=README,
    url='https://gitlab.com/chaosengine256/mini-jwt-backend',
    author='Chaos Engine',
    author_email='chaosengine256@gmail.com',
)
