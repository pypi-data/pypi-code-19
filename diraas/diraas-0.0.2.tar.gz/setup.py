from setuptools import setup, find_packages

setup(
    name='diraas',
    version='0.0.2',
    description='Make directory as a service.',
    author='wonder',
    author_email='wonderbeyond@gmail.com',
    url='',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'Flask~=0.12.2',
    ],
    entry_points={
        'console_scripts': [
            'diraas = diraas.server:main',
        ],
    },
)
