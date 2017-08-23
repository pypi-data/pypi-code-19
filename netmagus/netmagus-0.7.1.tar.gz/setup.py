# coding=utf-8
from setuptools import find_packages, setup

setup(name='netmagus',
      version='0.7.1',
      description='Python module for JSON data exchange via files or RPC with '
                  'the Intelligent Visibility NetMagus system.',
      url='http://www.intelligentvisibility.com/netmagus/',
      author='Richard Collins',
      author_email='richardc@intelligentvisibility.com',
      license='MIT',
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
      packages=find_packages(exclude=['tests*', 'examples']),
      install_requires=['future == 0.16.0',
                        'autobahn-sync == 0.3.2'
                        ]
      )
