import setuptools

import sys
if not sys.version_info[0] == 3:
    sys.exit("Sorry, only python version 3 is supported")

setuptools.setup(
    name='pysigfd',
    version='1.3.3',
    description='pysigfd is a module to help you deal with signals within python using the linux signal file \
    description construct',
    long_description='pysigfd is a module to help you deal with signals within python using the linux signal file description construct',
    url='https://github.com/veltzer/pysigfd',
    author='Mark Veltzer',
    author_email='mark.veltzer@gmail.com',
    license='PSF',
    classifiers=[
    ],
    keywords='signalfd python3 linux',
    packages=setuptools.find_packages(),
    install_requires=[
        'cffi',
    ],
)
