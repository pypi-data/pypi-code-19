from setuptools import (setup,
                        find_packages)

setup(name='ethereum_helpers',
      packages=find_packages(),
      version='0.0.3',
      description='Helper functions for working with ethereum network.',
      author='Azat Ibrakov',
      author_email='azatibrakov@gmail.com',
      url='https://github.com/lycantropos/ethereum_helpers',
      download_url='https://github.com/lycantropos/ethereum_helpers/archive/'
                   'master.tar.gz',
      keywords=['ethereum'],
      install_requires=[
          'ecdsa>=0.13',
          'scrypt>=0.8.0',
          'pycryptodomex>=3.4.6',
      ],
      setup_requires=['pytest-runner'],
      tests_require=[
          'pydevd',  # debugging
          'pytest>=3.0.5',
          'pytest-cov>=2.4.0',
          'hypothesis>=3.13.0',
          'pytz'  # working with datetime objects in hypothesis
      ])
