from setuptools import setup, find_packages
import sys, os

version = '0.0.3'

setup(name='htmlele',
    version=version,
    descriptio="create HTML files of website",
    long_description="""\
    create HTML files of website""",
    classifiers=[
        'Programming Language :: Python :: 3.6'
    ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='HTML files',
    author='katolele',
    author_email='katolele@katolele.net',
    url='http://katolele.net/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    # -*- Extra requirements: -*-
    'hinomaru',
    ],
    entry_points="""
    [console_scripts]
    htmlele = htmlele.mkpage:main
    """,
)
