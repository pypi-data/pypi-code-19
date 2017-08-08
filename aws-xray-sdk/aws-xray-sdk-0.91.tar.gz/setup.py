from setuptools import setup, find_packages
from os import path
import codecs

CURRENT_DIR = path.abspath(path.dirname(__file__))

with codecs.open(path.join(CURRENT_DIR, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aws-xray-sdk',
    version='0.91',

    description='The AWS X-Ray SDK for Python (the SDK) enables Python developers to record and emit information from within their applications to the AWS X-Ray service.',
    long_description=long_description,

    url='https://docs.aws.amazon.com/xray-sdk-for-python/latest/reference',

    author='Amazon Web Services',

    license="Apache License 2.0",

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    install_requires=['jsonpickle', 'wrapt', 'requests'],

    keywords='aws xray sdk',

    packages=find_packages(exclude=['tests*']),
    include_package_data=True
)
