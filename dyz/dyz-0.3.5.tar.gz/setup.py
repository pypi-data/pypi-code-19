from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = '0.3.5'

setup(
    name='dyz',
    version=version,
    description="SDYZ",
    long_description=README,
    classifiers=[
    ],
    keywords='dyz',
    author='Me',
    author_email='me@example.org',
    url='https://example.org',
    license='LGPL v3',
    py_modules=['dyz'],
    include_package_data=True,
    install_requires=[
        'click',
        'odoorpc',
        'prettytable',
        'ConfigParser',
        'XlsxWriter',
        'lxml',
    ],
    entry_points='''
        [console_scripts]
        dyz=dyz:main
    ''',
)
