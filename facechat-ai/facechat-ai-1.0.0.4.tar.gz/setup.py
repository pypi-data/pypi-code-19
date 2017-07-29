from distutils.core import setup
from setuptools import find_packages
setup(
	name = 'facechat-ai',
	version = '1.0.0.4',
	packages = find_packages(),
	py_modules = [
		'facechat/ai/autoencoder/agn',
		'facechat/ai/autoencoder/test',
		'facechat/ai/simple/softmax',
		'facechat/ai/web/api',
		'facechat/ai/data/reader',
		'facechat/ai/data/writer',
		'facechat/ai/tool/properties',
		'facechat/ai/cnn/mnist',
	],
	author = 'geekbruce',
	author_email = 'bruce.shaoheng@gmail.com',
	url = 'http://tikiapp.im',
	description = 'this is the facechat-ai which can help you build the deeplearning quickly',
)
