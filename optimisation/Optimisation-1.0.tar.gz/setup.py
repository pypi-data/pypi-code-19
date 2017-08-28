from setuptools import setup

setup(
	name = 'Optimisation',
	version = '1.0',
	description = 'Cellular Optimisation Functions',
	long_description = 'Set of functions built for foundations of Cellular Optimisation algorithm building and model builing and prediction',
	author = 'Joshin Smith',
	author_email = 'joshins@pepkor.co.za',
	license = 'MIT',
	packages = ['ModelBuild', 'ModelPrediction'],
	install_requires = ['pandas', 'numpy', 'patsy', 'statsmodels'],
	classifiers = ['Development Status :: 4 - Beta',
				'Natural Language :: English',
				'Intended Audience :: Manufacturing',
				'Operating System :: OS Independent',
				'Programming Language :: Python',
				'Topic :: Other/Nonlisted Topic',
				'Topic :: Scientific/Engineering :: Information Analysis'])