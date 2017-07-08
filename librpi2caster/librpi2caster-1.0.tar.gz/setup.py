"""librpi2caster common classes, functions and constants"""
from setuptools import setup

__version__ = '1.0'
__author__ = 'Christophe Slychan'
__author_email__ = 'krzysztof.slychan@gmail.com'
__github_url__ = 'http://github.com/elegantandrogyne/librpi2caster'

with open('README.rst', 'r') as readme_file:
    long_description = readme_file.read()

setup(name='librpi2caster', version=__version__,
      description='Common library for rpi2caster utility and drivers',
      long_description=long_description,
      url=__github_url__, author=__author__, author_email=__author_email__,
      license='MIT', zip_safe=True, packages=['librpi2caster'],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 3 :: Only'])
