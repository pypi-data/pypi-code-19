from setuptools import setup, find_packages

description = 'Project Caretaker. Inspired by npm.'

install_requirements = []

setup(
    name='pk',
    author='Amjith',
    author_email='amjith.r@gmail.com',
    version='0.0.0',
    license='BSD',
    packages=find_packages(),
    description=description,
    long_description=open('README.md').read(),
    install_requires=install_requirements,
)
