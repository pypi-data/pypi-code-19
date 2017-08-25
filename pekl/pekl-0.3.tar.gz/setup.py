from setuptools import setup

setup(name='pekl',
      version='0.3',
      description='An AWS Lambda library for making invocations and responses with large bodies easier.',
      url='https://github.com/tamme-io/pekl',
      author='tamme',
      author_email='opensource@tamme.io',
      license='MIT',
      packages=[
            'pekl'
      ],
      install_requires=[
            'boto3',
            'netaddr'
      ],
      zip_safe=False)
