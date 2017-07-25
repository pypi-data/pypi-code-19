from distutils.core import setup
from setuptools import find_packages
setup(
	name = 'ai-libs',
	version = '1.0.0.5',
	packages = find_packages(),
	py_modules = [
		'ai/autoencoder/agn_autoencoder',
		'ai/autoencoder/test',
		'ai/simple/softmax',
		'ai/web/api',
	],
	author = 'geekbruce',
	author_email = 'bruce.shaoheng@gmail.com',
	url = 'http://tikiapp.im',
	description = 'this is the ai-libs which can help you build the deeplearning quickly',
)
