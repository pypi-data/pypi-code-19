import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='mini-django-accounts',
    version='17.7.2',
    packages=find_packages(),
    install_requires=['django>=1.9.7'],
    include_package_data=True,
    license='MIT',
    description='A simple replacement for django.auth.user',
    long_description=README,
    url='https://gitlab.com/chaosengine256/mini-django-accounts',
    author='Chaos Engine',
    author_email='chaosengine265@gmail.com',
)
