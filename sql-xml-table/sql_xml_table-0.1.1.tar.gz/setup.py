from setuptools import setup, find_packages

setup(
    name='sql_xml_table',
    version='0.1.1',
    packages=find_packages(),
    python_requires=">=2.6, <4",
    install_requires=['python-sql', 'pymysql'],

    author='Wolfang Torres',
    author_email='wolfang.torres@gmail.com',
    url='https://github.com/WolfangT/sql_xml_table',
    license='GNU',
    keywords='SQL XML Table MySQL SQLite3',
    description='Small Python2/3 module to easily work with tables and \
import/export them to/from SQL databases and XML files',
    long_description = open('README.md').read(),
    )
