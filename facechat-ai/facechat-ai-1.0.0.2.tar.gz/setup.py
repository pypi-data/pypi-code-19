from distutils.core import setup
from setuptools import find_packages
setup(
	name = 'facechat-ai',
	version = '1.0.0.2',
	packages = find_packages(),
	py_modules = [
		'facechat/ai/autoencoder/agn',
		'facechat/ai/autoencoder/test',
		'facechat/ai/simple/softmax',
		'facechat/ai/web/api',
		'facechat/ai/data/input',
	],
	author = 'geekbruce',
	author_email = 'bruce.shaoheng@gmail.com',
	url = 'http://tikiapp.im',
	description = 'this is the ai-libs which can help you build the deeplearning quickly',
)
