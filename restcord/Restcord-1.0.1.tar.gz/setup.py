from setuptools import setup
import re, os, sys
from restcord.vars import __version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

requirements = []
with open('requirements.txt') as f:
  requirements = f.read().splitlines()

version = __version__
if not version:
    raise RuntimeError('version is not set')

readme = ''
with open('README.md') as f:
    readme = f.read()

setup(name='Restcord',
      author='JustMaffie',
      version=version,
      packages=['restcord'],
      license='MIT',
      description='Restcord is a rest API wrapper for the Discord API, but this one doesn\'t include WebSockets, this is for people who dont want websockets but only make requests to the api.',
      long_description=readme,
      url="https://github.com/JustMaffie/Restcord",
      include_package_data=True,
      install_requires=requirements,
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
      ]
)
