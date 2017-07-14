"""

TARGET

"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyTARGET',
    version='0.0.2',
    description='neTwork bAsed enRichment of Gene sETs',
    long_description=long_description,
    url='',
    author='Feng Zhang',
    author_email='15110700005@fudan.edu.cn',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for,

        
        'License :: OSI Approved :: MIT License',


        
        'Programming Language :: Python :: 2.7',
       
    ],

    
    keywords='Gene sets enrichment',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    
    install_requires=[
        "numpy",
        "scipy",
        "statsmodels",
    ],    


    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },


)
