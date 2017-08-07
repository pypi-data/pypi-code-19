# Based on PyPA sampleproject setup.py
# https://github.com/pypa/sampleproject/blob/master/setup.py

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the readme file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='TVRegex',
    version='0.1.1',
    description='Regex-only TV show renamer. No TVDB required!',
    long_description=long_description,
    author='Ryan Oldford',
    author_email='ryan.oldford@gmail.com',
    url='https://github.com/ROldford/tvregex',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[],
    python_requires='>=3',
    package_data={'tvregex': ['shownames.json']},
    entry_points={
        'console_scripts': [
            'tvregex=tvregex:main'
        ]
    }
)
