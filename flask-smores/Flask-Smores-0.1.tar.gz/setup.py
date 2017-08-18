"""
Flask-Smores
-------------

Validate inputs and document routes using marshmallow schemas
"""
from setuptools import setup


setup(
    name='Flask-Smores',
    version='0.1',
    url='',
    license='BSD',
    author='Nat Foster',
    author_email='nat.foster@gmail.com',
    description='Validate inputs and document routes using marshmallow schemas',
    long_description=__doc__,
    py_modules=['flask_smores'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'Marshmallow'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)