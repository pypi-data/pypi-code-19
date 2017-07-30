from setuptools import setup, find_packages
from os import path

VERSION = '0.2.0'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dphoyes.gicosf',
    version=VERSION,
    description='Tool for deploying Symfony projects over sftp',
    long_description=long_description,
    url='https://github.com/dphoyes/gicosf',
    download_url='https://github.com/dphoyes/gicosf/archive/v%s.tar.gz' % VERSION,
    author='David Hoyes',
    author_email='dphoyes@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='git composer sftp symfony dandelion deployment',
    py_modules=["gicosf"],
    install_requires=['dphoyes.libssh2', 'pyyaml', 'argcomplete', 'paramiko'],
    entry_points={
        'console_scripts': [
            'gicosf=gicosf:main',
        ],
    },
)
