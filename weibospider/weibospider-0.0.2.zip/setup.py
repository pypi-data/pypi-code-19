# coding=utf-8

from setuptools import setup, find_packages

VERSION = '0.0.2'

setup(
    name='weibospider',
    version="0.0.2",
    description=(
        'A simple but powerful spider for sinaweibo.'
        'For more information or comprehensive instructions, please contact at my email'
    ),
    author='wang xiaowei',
    author_email='3233069648@qq.com',
    maintainer='wang xiaowei',
    maintainer_email='3233069648@qq.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/SuperSaiyanSSS/SinaWeiboSpider',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'requests',
        'bs4',
        'lxml',
    ],
)

