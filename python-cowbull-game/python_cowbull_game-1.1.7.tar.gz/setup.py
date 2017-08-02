from setuptools import setup

setup(name='python_cowbull_game',
      version='1.1.7',
      description='Python cowbull game object',
      url='https://github.com/dsandersAzure/python_cowbull_game',
      author='David Sanders',
      author_email='dsanderscanadanospam@gmail.com',
      license='Apache License 2.0',
      packages=['python_cowbull_game'],
      install_requires=[
          'python-digits',
          'jsonschema',
      ],
      zip_safe=False)
