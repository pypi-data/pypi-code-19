from setuptools import setup

setup(
  name = 'Pygroove',
  packages = ['pygroove'], 
  version = '1.0',
  description = 'A python wrapper for Microsoft Groove Music API',
  author = 'P G Nithin Reddy',
  author_profile='https://github.com/rednithin',
  author_email = 'reddy.nithinpg@live.com',
  license='MIT',
  url = 'https://github.com/rednithin/Pygroove', 
  download_url = 'https://github.com/rednithin/Pygroove/archive/1.0.tar.gz', 
  keywords = ['Groove Music', 'Groove', 'API'], 
  classifiers = [
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3.6'
  ],
  install_requires=[
      'requests==2.18.3'
  ]
)
