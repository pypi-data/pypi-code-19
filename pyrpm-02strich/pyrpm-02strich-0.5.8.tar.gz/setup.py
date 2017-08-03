from setuptools import setup, find_packages

NAME = 'pyrpm-02strich'
VERSION = '0.5.8'
RELEASE = '1'

setup(name=NAME,
      version=VERSION,
      description="A pure python rpm reader and YUM metadata generator",
      author="Stefan Richter",
      author_email="stefan@02strich.de",
      url="https://github.com/02strich/pyrpm",
      license="BSD",

      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development :: Libraries',
      ],

      packages=find_packages(where='src'),
      package_dir={'': 'src'},
      options={
          'bdist_rpm': {
              'build_requires': [
                  'python',
                  'python-setuptools',
              ],
              'release': RELEASE
          },
      },
      install_requires=['future', ],
      test_suite="tests",
      )
