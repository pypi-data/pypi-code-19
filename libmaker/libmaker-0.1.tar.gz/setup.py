
from setuptools import setup

setup(
      name='libmaker',    # This is the name of your PyPI-package.
      keywords='library create make easy',
      version='0.1',
      description='A library that makes making libraries and uploading them to pypi easy',
      long_description=open('README.txt').read(),
      scripts=['code.py']                  # The name of your scipt, and also the command you'll be using for calling it
)
        