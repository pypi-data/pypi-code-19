import re

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'midipacks', '__init__.py'), encoding='utf-8') as fp:
  rex = r'^__version__ = \((\d+?), (\d+?), (\d+?)\)$'
  vtp = re.search(rex, fp.read(), re.M).groups()
  __version__ = '.'.join(vtp)

install_requires = ('mido', 'python-rtmidi',)
setup_requires = ('pytest-runner',)
test_requirements = ('pytest',)


setup(
  name='midipacks',
  version=__version__,
  description='Packets over MIDI',
  url='https://github.com/prashnts/midipacks',
  download_url='https://github.com/prashnts/midipacks/tarball/' + __version__,
  license='MIT',
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Software Development :: Libraries :: Python Modules'
  ],
  packages=['midipacks'],
  author='Prashant Sinha',
  install_requires=install_requires,
  setup_requires=setup_requires,
  tests_require=test_requirements,
  author_email='prashant@noop.pw',
  include_package_data=True,
)
