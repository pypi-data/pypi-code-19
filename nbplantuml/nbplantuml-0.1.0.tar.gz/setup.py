from setuptools import setup

setup(name='nbplantuml',
      version='0.1.0',
      description='Easily embed plantuml diagrams in your IPython noteboooks',
      author='Eyal Firstenberg',
      author_email='eyalfir@gmail.com',
      classifiers=['Development Status :: 4 - Beta'],
      packages=['nbplantuml'],
      install_requires=['plantuml', 'ipython'])
