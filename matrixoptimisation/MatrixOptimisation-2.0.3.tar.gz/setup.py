from setuptools import setup

setup(name = 'MatrixOptimisation', 
	version = '2.0.3',
	description = 'Series of Functions Designed for Cellular Optimisation',
	author = 'Joshin Smith',
	author_email = 'joshins@pepkor.co.za',
	license = 'MIT',
	packages = ['MatrixOptimisation'],
	install_requires = ['pandas', 'numpy'],
	classifiers = ['Development Status :: 5 - Production/Stable',
		'Natural Language :: English'
	])