from distutils.core import setup
from setuptools import find_packages
setup(
	name = 'ai-libs',
	version = '1.0.0.3',
	packages = find_packages(),
	py_modules = [
		'ai/autoencoder/agn_autoencoder',
		'ai/autoencoder/test'
	],
	author = 'geekbruce',
	author_email = 'bruce.shaoheng@gmail.com',
	url = 'http://tikiapp.im',
	description = 'the simple test',
)
