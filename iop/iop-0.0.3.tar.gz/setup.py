from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='iop',
    version='0.0.3',
    description='Input-Output processing: Apache Camel on python',
    long_description=long_description,
    url='https://github.com/reddec/iop',
    author='Baryshnikov Alexander',
    author_email='dev@baryshnikov.net',
    packages=find_packages(),
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='camel iop',
    install_requires=['setuptools>=30', 'jinja2>=2.9.0', 'aioimaplib>=0.7.11'],
    entry_points={
        'console_scripts': [
            'iop=iop.runner.main:main'
        ]
    }
)
