# -*- coding:utf-8 -*-
from os.path import dirname, join
from pkg_resources import parse_version
from setuptools import setup, find_packages, __version__ as setuptools_version

with open(join(dirname(__file__), 'alphahome/VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()

extras_require = {}

setup(
    name='alphahome',
    version=version,
    url='https://alphaho.me',
    description='An SDK for AlphaHome smart home open platform.',
    long_description=open('README.rst').read(),
    author='AlphaHome developers',
    maintainer='Tim Kong',
    maintainer_email='yjxkwp@foxmail.com',
    license='BSD',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['alphahome = alphahome.cmdline:execute']
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'oss2',
        'django',
        'requests',
        'djangorestframework'
    ],
    extras_require=extras_require,
)
