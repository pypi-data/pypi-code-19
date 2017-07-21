#!/usr/bin/env python

from setuptools import find_packages, setup


setup(
    name='django_settings_helper',

    version='1.0.4',

    url='https://github.com/chwnam/django_settings_helper',

    author='changwoo',

    author_email='ep6tri@hotmail.com',

    description='A simple django\'s settings value helper',

    long_description='',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Environment :: Web Environment',

        'Framework :: Django',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.5',
    ],

    keywords='django settings helper',

    packages=find_packages(exclude=[]),

    install_requires=[],

    extras_require={

    },

    package_data={},

    data_files=[],

    entry_points={

    },
)
