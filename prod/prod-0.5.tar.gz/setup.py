
from setuptools import setup

setup(
      name='prod',    # This is the name of your PyPI-package.
      keywords='product sum',
      version='0.5',
      description='If they have sum(), why not product()',
      long_description=open('README.txt').read(),
      scripts=['u.py']                  # The name of your scipt, and also the command you'll be using for calling it
)
        