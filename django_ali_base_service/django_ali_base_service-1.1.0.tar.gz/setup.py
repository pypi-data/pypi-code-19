import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django_ali_base_service',
    version='1.1.0',
    packages=find_packages(),
    install_requires=[
        'djangorestframework==3.5.3',
    ],
    include_package_data=True,
    license='BSD License',
    description='A base code for building webservices for django models based on Django Rest Framework',
    long_description=README,
    author='Alireza Ahmadi',
    author_email='alirezaahmadi69@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
