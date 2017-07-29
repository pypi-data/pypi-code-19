from distutils.core import setup

setup(
	name='listorm',
	version='0.0.6',
	description='SQL ORM API for table type of Python dict-list',
	author = 'HS Moon',
	author_email = 'mhs9089@gmail.com',
	py_modules = ['listorm'],
	install_requires=['xlrd', 'xlsxwriter'],
	url='https://github.com/zwolf21/listorm'
)