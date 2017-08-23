from setuptools import setup

setup(name = 'OptimisationFunctions', 
	version = '2.1.3',
	long_description = '''Series of Functions Designed for Cellular Optimisation 
							model building and prediction''',
	author = 'Joshin Smith',
	author_email = 'joshins@pepkor.co.za',
	license = 'MIT',
	packages = ['GLM_Model_Predictions', 'GLM_Model_Build'],
	install_requires = ['pandas', 'numpy'],
	classifiers = ['Development Status :: 5 - Production/Stable',
		'Natural Language :: English'
	])