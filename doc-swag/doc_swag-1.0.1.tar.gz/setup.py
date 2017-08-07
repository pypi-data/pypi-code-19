import re
import os


from distutils.core import setup


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return open(fpath(fname)).read()


setup(
    name='doc_swag',
    version='1.0.1',
    license='MIT',
    author='Ayush',
    author_email='ayushkatara93@gmail.com',
    description='Extract swagger specs from your flask project',
    packages=['doc_swag'],
    package_data      = {'doc_swag': ['*']},
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=0.10',
        'PyYAML>=3.0',
        'jsonschema>=2.5.1',
        'mistune',
        'six>=1.10.0'
    ]
)
