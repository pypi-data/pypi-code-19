
from setuptools import setup

setup(
      name='ploopy',    # This is the name of your PyPI-package.
      keywords='ploopy say',
      version='9',
      description='ploopyness',
      long_description=open('README.txt').read(),
      scripts=['code.py']                  # The name of your scipt, and also the command you'll be using for calling it
)
        