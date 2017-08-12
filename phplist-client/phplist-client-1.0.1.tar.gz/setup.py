# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

#with open(path.join(here, 'README.md'), encoding='utf-8') as f:
#    long_description = f.read()
def read_md(filename):
    import pypandoc
    return pypandoc.convert('README.md', 'rst')

setup(
    name='phplist-client',
    version='1.0.1',

    description='Python client for the phplist REST API',
    long_description=read_md('README.md'),

    # The project's main homepage.
    url='https://github.com/tubaman/phplist-restapi-python',

    author='Ryan Nowakowski',
    author_email='tubaman@fattuba.com',

    # Choose your license
    license='Apache 2.0',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='phplist rest client',

    py_modules=["phplist"],
    install_requires=['requests', 'pypandoc'],
    setup_requires=['pypandoc'],
    extras_require={
        'dev': ['ipython'],
        'test': ['nose'],
    },
)
