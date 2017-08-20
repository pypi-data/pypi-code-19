import os

import friend

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def readme():
    try:
        import pypandoc
        return pypandoc.convert(source='README.md', to='rst')
    except:
        with open('README.md') as f:
            return f.read()

version = friend.__version__

config = {
    'description': 'Python utility library',
    'long_description': readme(),
    'author': 'Joseph Wright',
    'url': 'https://github.com/cloudboss/friend',
    'download_url': 'https://github.com/cloudboss/friend/releases/{}'.format(version),
    'author_email': 'joseph@cloudboss.co',
    'version': version,
    'packages': ['friend'],
    'name': 'friend',
    'test_suite': 'tests',
}

setup(**config)
