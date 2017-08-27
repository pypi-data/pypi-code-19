from distutils.core import setup

setup(
	name='django-slicepaginator',
	version='0.0.2',
	description='Slice page_range of default django paginator.page_range',
	author = 'HS Moon',
	author_email = 'mhs9089@gmail.com',
	py_modules = ['djangoslicer'],
	url='https://github.com/zwolf21/django-slicepaginator'
)

'''
python setup.py sdist
twine upload dist/*

'''