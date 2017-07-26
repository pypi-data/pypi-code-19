from setuptools import setup, find_packages
import re

version = ''
with open('opfront/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Version is not set')

readme = 'See https://github.com/opfront/python-sdk for README.'

setup(
    name='opfront',
    author='opfront',
    url='https://github.com/opfront/python-sdk',
    version=version,
    packages=find_packages(),
    license='MIT',
    description='Python SDK for the Opfront REST API',
    long_description=readme,
    install_requires=[
        "requests==2.17.3"
    ]
)
