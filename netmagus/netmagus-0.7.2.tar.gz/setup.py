# coding=utf-8
from setuptools import find_packages, setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'future == 0.16.0',
    'autobahn-sync == 0.3.2'
]

test_requirements = [
    'pytest'
]

setup(name='netmagus',
      version='0.7.2',
      description='Python module for JSON data exchange via files or RPC with '
                  'the Intelligent Visibility NetMagus system.',
      long_description=readme + '\n\n' + history,
      url='http://www.intelligentvisibility.com/netmagus/',
      author='Richard Collins',
      author_email='richardc@intelligentvisibility.com',
      license='GNU lGPLv3',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: GNU Lesser General Public License v3 '
          'or later (LGPLv3+)',
          'Natural Language :: English',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: System :: Networking'
      ],
      keywords='netmagus network automation netops',
      packages=find_packages(include=['netmagus']),
      include_package_data=True,
      install_requires=requirements,
      test_suite='tests',
      tests_require=test_requirements
      )
