from setuptools import setup, find_packages
import codecs
from os import path

__version__ = '2017.8.20'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with codecs.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with codecs.open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name='image_attendant',
    version=__version__,
    description='Helpful image processing functions',
    long_description=long_description,
    url='https://github.com/who8mylunch/image_attendant',
    license='MIT',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3',
    ],
    keywords='',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='Pierre V. Villeneuve',
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email='pierre.villeneuve@gmail.com'
)
