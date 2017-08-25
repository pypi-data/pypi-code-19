# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
This package contains the exampleblock Sphinx extension.
'''

requires = ['Sphinx>=1.0']

setup(
    name='sphinxcontrib-exampleblock',
    version='0.0.1',
    url='https://github.com/testthedocs/sphinxcontrib-exampleblock',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-exampleblock',
    license='BSD',
    author='Sven Strack',
    author_email='info@testthedocs.org',
    description='Sphinx "exampleblock" extension',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Documentation',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
