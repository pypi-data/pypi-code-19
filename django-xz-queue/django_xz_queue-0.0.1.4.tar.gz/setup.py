# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='django_xz_queue',
    version='0.0.1.4',
    author='xingzhe',
    author_email='developer@bi-ci.com',
    packages=['django_xz_queue'],
    url='https://github.com/AoAoStudio/django_xz_queue',
    license='MIT',
    description='An Django app that provides django integration for aliyun-mns/redis',
    zip_safe=False,
    include_package_data=True,
    package_data={'': ['README']},
    install_requires=[''],
    dependency_links=['https://github.com/AoAoStudio/aliyun-mns-sdk/tarball/master#egg=aliyun-mns-sdk-1.1.4'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
