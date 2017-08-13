from setuptools import setup
import os

requirements = os.path.join(os.path.dirname(__file__), 'requirements.txt')

setup(
    name='uvspotify',
    version='0.4',
    description='Spotify client for uvhttp',
    url='https://github.com/justinbarrick/uvspotify',
    packages=['uvspotify'],
    install_requires=[ r.rstrip() for r in open(requirements).readlines() ]
)
