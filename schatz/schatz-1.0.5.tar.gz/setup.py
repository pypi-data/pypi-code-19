from setuptools import setup

setup(
    name='schatz',
    version='1.0.5',
    license='Apache 2.0',
    maintainer='Egor Litvinenko',
    maintainer_email='e.v.litvinenko.1@gmail.com',
    packages=['schatz'],
    description='Schatz integration package for Python 3',
    install_requires=[
        'requests',
        'SQLAlchemy',
        'sqlalchemy-clickhouse',
    ]
)