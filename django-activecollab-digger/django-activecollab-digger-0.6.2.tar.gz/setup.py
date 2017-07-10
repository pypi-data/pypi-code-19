"""
A setuptools based setup module.

See:
    https://packaging.python.org/en/latest/distributing.html
    https://github.com/pypa/sampleproject
    """

from codecs import open
from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-activecollab-digger',

    version='0.6.2',

    description='Django ActiveCollab application',
    long_description=long_description,

    url='https://github.com/kingsdigitallab/django-activecollab-digger',

    author='King\'s Digital Lab',
    author_email='kdl-info@kcl.ac.uk',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
    ],

    keywords='django activecollab',

    packages=['activecollab_digger'],

    install_requires=['requests[security]', 'simplejson'],

    package_data={
        'activecollab_digger': [
            'static/activecollab_digger/js/app.js',
            'static/vendor/bulma/css/bulma.css',
            'static/vendor/bulma/css/bulma.css',
            'static/vendor/bulma/css/bulma.css.map',
            'static/vendor/font-awesome/css/font-awesome.min.css',
            'static/vendor/font-awesome/fonts/*.*',
            'static/vendor/tiny-cookie/tiny-cookie.min.js',
            'static/vendor/vue/dist/vue.min.js',
            'templates/activecollab_digger/*.html'
        ],
    },
)
