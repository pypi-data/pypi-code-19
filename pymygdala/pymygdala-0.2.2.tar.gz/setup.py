# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

NAME = 'pymygdala'
HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'README.md')) as f:
    README = f.read()
with open(os.path.join(HERE, 'CHANGES.txt')) as f:
    CHANGES = f.read()
with open(os.path.join(HERE, NAME, '_version.py')) as f:
    VERSION = f.readlines()[-1].split()[-1].strip("\"'")

INST_REQUIRES = [ 'pika==0.10.0',
                  'pycapo==0.1.1',
                  'python-dateutil==2.6.0',
                  'simplejson==3.11.1']
TESTS_REQUIRES = ['pytest==3.0.5']
SETUP_REQUIRES = ['pytest-runner==2.9']

setup(name=NAME,
      version=VERSION,
      description='Pymygdala: Archive messaging for Python',
      long_description=README + '\n\n' + CHANGES,
      author='Daniel K Lyons',
      author_email='dlyons@nrao.edu',
      url='https://open-bitbucket.nrao.edu/projects/SSA/repos/pymygdala',
      keywords='',
      license='GPL',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',

          # probably not the best topic, unsure what else to puy here
          'Topic :: Software Development :: Build Tools',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
      ],
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite=None,
      install_requires=INST_REQUIRES,
      tests_require=TESTS_REQUIRES,
      setup_requires=SETUP_REQUIRES,
      entry_points={
          'console_scripts': [
              'pym-sendevent = pymygdala.commands:sendevent',
              'pym-dumplogs = pymygdala.commands:dumplogs',
              'pym-sendlog = pymygdala.commands:sendlog',
          ]
      },
      )
