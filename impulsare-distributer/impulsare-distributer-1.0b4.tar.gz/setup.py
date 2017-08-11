from setuptools import setup, find_packages
from codecs import open
from os import path

__version__ = '1.0b4'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '')
                    for x in all_reqs if x.startswith('git+')]

setup(
    name='impulsare-distributer',
    version=__version__,
    description='A distributer that helps to publish to a queue and process tasks from a queue',
    long_description=long_description,
    url='https://github.com/impulsare/distributer',
    download_url='https://github.com/impulsare/distributer/tarball/' + __version__,
    license='AGPLv3',
    classifiers=[
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Systems Administration',
    ],
    entry_points='''[console_scripts]
queue-listener=impulsare_distributer.queue_listener:main''',
    keywords='distributer,python,redis,impulsare,rq,esb,etl',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='Emmanuel Dyan',
    author_email='emmanuel@impulsare.io',
    install_requires=install_requires,
    dependency_links=dependency_links
)
