# coding: utf-8
__author__ = 'jiyue'

from setuptools import setup, find_packages, Extension
from scikit_credit import version

packages = [
    'scikit_credit.encoder',
]

setup(
    name='scikit-credit',
    version=version,
    description='scikit-credit for qudian',
    author='Yue Ji',
    author_email='jiyue@quandian.com',
    url='https://git.qufenqi.com/risk-data-scientist/scikit-credit',
    keywords='scikit credit',
    license='MIT',
    packages=find_packages(exclude=['test']),
    package_dir={'scikit-credit': 'src'},
    install_requires=['scikit-learn', 'pandas', 'numpy', 'scipy']
)
