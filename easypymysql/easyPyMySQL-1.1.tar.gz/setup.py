from setuptools import setup, find_packages
from distutils.core import setup
# install_requires=["bs4","pymysql"]
# include_package_data=True
# package_data = ['demo']

setup(
    name="easyPyMySQL",
    version="1.1",
    description="简单易用的数据库ORM模块",
    url='https://github.com/AkiYama-Ryou/easyPyMySQL',
    author="ChenRuohan",
    author_email='crh51306@gmail.com',
    packages= ['easyPyMySQL'],
    )

# setup(
#     name='easyPyMySQL',
#     version='1.0',
#     keywords = ('mysql', 'orm'),
#     description='简单易用的数据库ORM模块',
#     license='Free',
#     author='ChenRuohan',
#     author_email='crh51306@gmail.com',
#     url='https://github.com/AkiYama-Ryou/easyPyMySQL',
#     platforms = 'mysql',
#     packages = find_packages(),
#     package_dir = {'demo':'demo'}
# )

