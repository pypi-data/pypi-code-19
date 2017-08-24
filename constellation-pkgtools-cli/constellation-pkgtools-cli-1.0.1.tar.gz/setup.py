from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='constellation-pkgtools-cli',
    version='1.0.1',
    description='Constellation Package Tools CLI',
    long_description=long_description,
    url='https://developer.myconstellation.io',
    author='Sebastien Warin',
    author_email='support@myconstellation.io',
    license='Apache',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='constellation package python tools development',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['docopt', 'requests'],
    entry_points={
        'console_scripts': [
            'ctln=constellationpkgtools:main',
        ],
    },
)

