#coding: utf8
from distutils.core import setup

setup(
    name='hg-formatsource',
    version='0.1.0',
    author='Octobus',
    author_email='contact@octobus.net',
    maintainer='Pierre-Yves David',
    maintainer_email='pierre-yves.david@octobus.net',
    url='https://bitbucket.org/octobus/hg-formatsource',
    description=('Mercurial extension to apply and gracefully merge code formatting'),
    long_description=open('README').read(),
    keywords='hg mercurial',
    license='GPLv2+',
    packages=['hgext3rd'],
)
