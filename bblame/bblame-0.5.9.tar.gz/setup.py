"""Setup script for building/installing package using distutils"""
from os import path
from setuptools import setup

PROG_NAME = 'bblame'
PACKAGE_NAME = 'betterblame'
# Use README as the long description
PROJECT_DIR = path.abspath(path.dirname(__file__))
with open(path.join(PROJECT_DIR, 'README.rst')) as f:
    LONG_DESCRIPTION = f.read()

# Load the __version__ string into the setup.py namespace with exec instead of
# importing, since there are known issues with the importing approach wreaking
# havoc in projects that have dependencies
__version__ = '0.0.0'  # default value and makes pylint happy
version_module = '%s/version.py' % PACKAGE_NAME
exec(open(version_module).read())

setup(name=PROG_NAME,
      # pylint: disable=undefined-variable
      version=__version__,
      description='An ncurses app for browsing file git history',
      long_description=LONG_DESCRIPTION,
      url='https://bitbucket.org/niko333/betterblame',
      author='Niko Oliveira',
      author_email='oliveira.n3@gmail.com',
      license='MIT',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Topic :: Software Development :: Build Tools',
                   'Environment :: Console :: Curses',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3'],
      keywords=['better git blame history curses ncurses'],
      packages=[PACKAGE_NAME],
      install_requires=[
          'texteditpad',
          'pygments',
          'future',
          'sh',
      ],
      scripts=[PROG_NAME],
      # entry_points={
      #     'console_scripts': [
      #         'bblame = bblame.bblame:main',
      #     ]
      # },
      zip_safe=False)
