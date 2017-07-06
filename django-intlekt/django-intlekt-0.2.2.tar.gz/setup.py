import os
from setuptools import setup, find_packages


def readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
        return f.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-intlekt',
    version='0.2.2',
    url='https://github.com/IEMLdev/django-intlekt',
    description='Django app for Intlekt, a content curation application using the IEML language.',
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Text Processing :: Indexing'
    ],
    author='Vincent Lefoulon',
    author_email='vincent.lefoulon@free.fr',
    keywords='ieml intlekt semantic syntax language indexing',
    license='GPLv3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'mongoengine',
        'blinker',  # For Mongoengine signals
        'django',
        'djangorestframework',
        'django-rest-framework-mongoengine',
        'drf-nested-routers',
        'pycountry',
        'python-slugify',
    ],
)
