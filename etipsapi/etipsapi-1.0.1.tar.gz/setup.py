""" e-tip5 API operations """
from setuptools import setup, find_packages
setup(
    name='etipsapi',
    version='1.0.1',
    packages=find_packages(),
    install_requires=['PyJWT', 'requests'],
    description='e-tips API',
    author='Justin Taylor',
    author_email='jtaylor@depoel.co.uk',
    url='https://bitbucket.org/leopardsoftware/pypi'
)
