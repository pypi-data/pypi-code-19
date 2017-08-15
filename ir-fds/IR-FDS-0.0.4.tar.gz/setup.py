#!/usr/bin/env python

from setuptools import setup


setup(
    name='IR-FDS',
    version='0.0.4',
    url='https://coding.net/u/lvzhaoxing/p/IR-FDS',
    license='MIT',
    author='Lv Zhaoxing',
    author_email='lvzhaoxing@qq.com',
    description='Convenient extension for Xiaomi File Storage Service',
    long_description='Convenient extension for Xiaomi File Storage Service. Please visit: https://coding.net/u/lvzhaoxing/p/IR-FDS',
    py_modules=['ir_fds'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    keywords='fds',
    #packages=[],
    package_data={'': ['LICENSE']},
    install_requires=[
        'setuptools',
        'galaxy-fds-sdk'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
