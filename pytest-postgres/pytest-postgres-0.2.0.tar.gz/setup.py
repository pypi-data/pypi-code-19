from setuptools import setup, find_packages


setup(
    name='pytest-postgres',
    version='0.2.0',
    packages=find_packages(),
    url='https://github.com/clayman74/pytest-postgres',
    licence='MIT',
    author='Kirill Sumorokov',
    author_email='sumorokov.k@gmail.com',
    description='Run PostgreSQL in Docker container in Pytest.',
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Testing",
        "Framework :: Pytest"
    ],

    install_requires=[
        'docker==2.5.1',
        'psycopg2',
        'pytest',
    ],

    entry_points={
        'pytest11': [
            'postgres = pytest_postgres.plugin'
        ]
    }
)
