from setuptools import setup

setup(
    name='schatz',
    version='0.1',
    license='Apache 2.0',
    maintainer='Egor Litvinenko',
    maintainer_email='e.v.litvinenko.1@gmail.com',
    packages=['schatz'],
    summary='Schatz integration package for Python 3',
    install_requires=[
        'requests',
        'SQLAlchemy',
        'sqlalchemy-clickhouse',
    ]
)