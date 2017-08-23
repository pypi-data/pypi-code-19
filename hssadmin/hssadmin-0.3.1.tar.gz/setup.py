from setuptools import setup


requires = [
    "requests>=2.14.2",
    "urllib3>=1.22",
    "pytz>=2017.2"
]


setup(
    name='hssadmin',
    version='0.3.1',
    description='Cloudian HyperStore(R) Admin API SDK for Python',
    long_description='This module is a Software Development Kit for Cloudian HyperStore Admin API. Please bear in mind that this module is NOT an official release from Cloudian Inc. and Cloudian K.K.',
    url='https://github.com/ryosuke-mt/hyperstore',
    author='Ryosuke Matsui',
    author_email='rmatsui@cloudian.com',
    maintainer='Ryosuke Matsui',
    maintainer_email='rmatsui@cloudian.com',
    license='MIT',
    keywords='sample setuptools development',
    packages=[
        "hssadmin"
    ],
    install_requires=requires,
    classifiers=[
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License'
    ],
)
