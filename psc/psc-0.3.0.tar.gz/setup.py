from setuptools import setup
import unittest

VERSION = "0.3.0"


def default_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


def run_test():
    test_suite = default_test_suite()
    test_suite.run()


setup(
    name='psc',
    version=VERSION,
    description='A cli credential/secret storage utility using EC2 SSM Parameter Store',
    license='MIT',
    url='https://github.com/smooch/parameter-store-client',
    author='Smooch',
    author_email='devs@smooch.io',
    scripts=['psc.py'],
    entry_points={
        'console_scripts': [
            'psc = psc:main'
        ]
    },
    py_modules=['psc'],
    install_requires=[
        'boto3>=1.1.1',
        'botocore>=1.4.85',
        'prettytable>=0.7.2'
    ],
    test_suite='setup.default_test_suite'
)
