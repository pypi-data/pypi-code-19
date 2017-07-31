from setuptools import setup, find_packages
from codecs import open
from os import path

__version__ = '0.0.1a'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '')
                    for x in all_reqs
                    if x.startswith('git+')]

setup(
    name='CrApsim',
    version=__version__,
    python_requires='>=3.6',
    description='Creates Apsim-Project files from given parameters and files.',
    long_description=long_description,
    url='https://neulaender.net',   # TBD
    download_url='https://neulaender.net/' + __version__,
    license='BSD',
    entry_points={
        'console_scripts': [
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: Free for non-commercial use',
        'Natural Language :: English',
        'Framework :: Pytest',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities',
    ],
    keywords='apsim climate agrar production simulator agricultural systems',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='Torsten Zielke',
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email='torsten.zielke@protonmail.com',
)
