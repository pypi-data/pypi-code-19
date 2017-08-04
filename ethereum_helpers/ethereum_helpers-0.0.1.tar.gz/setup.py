from setuptools import (setup,
                        find_packages)

setup(name='ethereum_helpers',
      packages=find_packages(),
      version='0.0.1',
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
      ])
