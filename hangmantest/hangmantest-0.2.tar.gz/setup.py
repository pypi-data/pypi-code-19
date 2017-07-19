
from setuptools import setup

setup(
      name='hangmantest',    # This is the name of your PyPI-package.
      keywords='',
      version='0.2',
      description='hangmanplayer',
      long_description=open('README.txt').read(),
      scripts=['code.py']                  # The name of your scipt, and also the command you'll be using for calling it
)
        