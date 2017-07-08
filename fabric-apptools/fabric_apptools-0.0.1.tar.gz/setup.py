import sys

from setuptools import setup

if sys.version_info.major < 3:
    raise NotImplementedError('use python 3.x')

import fabric_apptools

setup(name='fabric_apptools',
      version=fabric_apptools.__version__,
      description='',
      author=fabric_apptools.__author__,
      author_email='i2bskn@gmail.com',
      url='https://github.com/i2bskn/fabric-apptools',
      packages=['fabric_apptools'],
      install_requires=[
          'fabric3',
          'PyYAML',
          'Jinja2',
      ],
      license='MIT',
      classifiers=['Development Status :: 1 - Planning',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3',
                   ]
      )
