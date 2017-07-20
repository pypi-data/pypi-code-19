from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
    long_description = readme_file.read()

setup(
    name='ordering',
    version='0.1.0',
    description='A data structure to impose a total order on a collection of objects',
    long_description=long_description,
    url='https://github.com/madman-bob/python-order-maintenance',
    author='Robert Wright',
    author_email='madman.bob@hotmail.co.uk',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=['order', 'ordering'],
    packages=['ordering'],
    python_requires='>=3.6'
)
