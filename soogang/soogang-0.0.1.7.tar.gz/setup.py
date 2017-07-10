from distutils.core import setup

from setuptools import find_packages

setup(
    name='soogang',
    version='0.0.1.7',
    url='https://github.com/sougang/soogang-sdk',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "qiniu==7.1.4",
        "xlrd==1.0.0",
        'XlsxWriter==0.9.8',
    ],
    license='MIT',
    author='Ryan Wang',
    author_email='hwwangwang@gmail.com',
    description='soogang sdk'
)
