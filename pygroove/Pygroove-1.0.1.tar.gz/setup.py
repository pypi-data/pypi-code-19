from setuptools import setup

setup(
  name = 'Pygroove',
  packages = ['pygroove'], 
  version = '1.0.1',
  description = 'A python wrapper for Microsoft Groove Music API',
  author = 'P G Nithin Reddy',
  author_email = 'reddy.nithinpg@live.com',
  license='MIT',
  url = 'https://github.com/rednithin/Pygroove', 
  keywords = ['Groove Music', 'Groove', 'API'], 
  classifiers = [
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3.6'
  ],
  install_requires=[
      'requests==2.18.3'
  ]
)
