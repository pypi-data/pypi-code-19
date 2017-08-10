from setuptools import setup, find_packages
from codecs import open
from os import path

__version__ = '1.0b2'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name='impulsare-logger',
    version=__version__,
    description='A simple python logger that creates two handlers with a nice formatting : Stream and File',
    long_description="""A logger that sends its logs to rotated files + directly to console (configurable).""",
    url='https://github.com/impulsare/logger',
    download_url='https://github.com/impulsare/logger/tarball/' + __version__,
    license='AGPLv3',
    classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3',
    ],
    keywords='logger,python',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='Emmanuel Dyan',
    author_email='emmanuel@impulsare.io',
    install_requires=install_requires,
    dependency_links=dependency_links
)
