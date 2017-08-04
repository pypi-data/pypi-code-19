# -*- coding=utf-8 -*-

from distutils.core import setup

# setup(
#     name = 'hammer',
#     version = '0.0.1',
#     keywords = ('pip'),
#     description = 'lgq hammer tool',
#     long_description = 'lgq hammer tool',
#     license = 'MIT Licence',
#
#     url = 'http://awolfly9.com',
#     author = 'lgq',
#     author_email = 'awolfly9@gmail.com',
#
#     # packages = ['hammer'],
#     packages = find_packages(),
#     # include_package_data = True,
#     platforms = 'any',
#     install_requires = [],
#     scripts = ['./kill_port'],
# )


setup(
    name='lgqhammer',
    version='0.1',
    packages=['hammer', 'hammer.pymysqlpool'],
    url='http://awolfly9.com/',
    license='MIT Licence',
    author='lgq',
    author_email='awolfly9@gmail.com',
    requires=['pymysql', 'pandas'],
    description='MySQL connection pool utility.',
    scripts = ['./kill_port'],
)
