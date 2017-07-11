from setuptools import setup
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tes',
    version='1.1.1',
    packages=['es_commands'],
    include_package_data=True,
    install_requires=[
        'Click', 'Elasticsearch', 'Texttable'
    ],
    entry_points={
        'console_scripts': [
        'tes=es_commands.tes:cli',
        'tes:cat=es_commands.cat_api:cat',
        'tes:cluster=es_commands.cluster_api:cluster',
        'tes:node=es_commands.node_api:node'
        ]
        },
    author="Deepanshu Gupta",
    author_email="gupta.deeshu@gmail.com",
    description="Tool for Elasticsearch",
    long_description=long_description,
    url="https://github.com/deeshugupta/tes",
    download_url="https://github.com/deeshugupta/tes/archive/v1.1.1.tar.gz",
    keywords="tes elasticsearch Elasticsearch",
    license="GNU General Public License v3.0",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: System :: Monitoring',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
    ]
)
