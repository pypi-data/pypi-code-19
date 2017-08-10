from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

def readme():
    with open('README.org') as f:
        return f.read()

setup(
  name = 'GEOpurify',
  packages = ['GEOpurify'],
  version = '0.1',
  description = 'Making Gene Expression Omnibus data cleansing easy.',
  long_description=readme(),
  author = 'Sasha Illarionov',
  author_email = 'sasha.delly@gmail.com',
  license ='MIT',
  install_requires=requirements,
  url = 'https://github.com/biologos/GEOpurify',
  download_url = 'https://github.com/biologos/GEOpurify/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['GEO', 'bioinformatics'],
  include_package_data=True,
  classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6']
)
