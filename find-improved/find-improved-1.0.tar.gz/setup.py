#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='find-improved'
      ,url='https://bitbucket.org/adamlabadorf/fim/overview'
      ,version=open('VERSION').read().strip()
      ,description=('fIND imPROVED - a command line tool similar to xargs or '
        'find -exec for executing a command pattern on multiple inputs')
      ,author='Adam Labadorf'
      ,author_email='alabadorf@gmail.com'
      ,license='MIT'
      ,python_requires='>= 2.7, >= 3'
      ,packages=find_packages()
      ,install_requires=[
          'docopt'
      ]
      ,entry_points={
        'console_scripts': [
          'fim=fim:main'
        ]
      }
      ,setup_requires=['pytest-runner']
      ,tests_require=['pytest']
      ,classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 5 - Production/Stable',

          # Indicate who your project is intended for
          'Intended Audience :: System Administrators',
          'Topic :: Utilities',

          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: MIT License',

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',

	  'Environment :: Console'
      ]
     )
