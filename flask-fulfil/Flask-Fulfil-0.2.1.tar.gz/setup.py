'''
    Flask-Fulfil
    ------------
    Fulfil.IO for your Flask app
'''

from setuptools import setup

setup(
    name='Flask-Fulfil',
    version='0.2.1',
    url='https://github.com/fulfilio/flask-fulfil',
    license='BSD',
    author='Fulfil.IO Inc.',
    author_email='hello@fulfil.io',
    description='Fulfil.IO for Flask Apps',
    long_description=__doc__,
    packages=['flask_fulfil'],
    zip_safe=False,
    platforms='any',
    install_requires=['Flask', 'fulfil_client>=0.9.0'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
