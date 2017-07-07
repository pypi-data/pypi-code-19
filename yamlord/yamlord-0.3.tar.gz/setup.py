from setuptools import setup
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='yamlord',
    version='0.3',
    description='wrapper for yaml package to read/write OrderedDict',
    long_description=long_description,
    author='Ryan J. Dillon',
    author_email='ryanjamesdillon@gmail.com',
    url='https://github.com/ryanjdillon/yamlord',
    download_url='https://github.com/ryanjdillon/yamlord/archive/0.3.tar.gz',
    license='MIT',
    packages=['yamlord'],
    keywords=['python-3'],
    install_requires=['pyaml'],
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Programming Language :: Python :: 3.5'],
    zip_safe=False)
