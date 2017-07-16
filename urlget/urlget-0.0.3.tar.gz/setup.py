from distutils.core import setup

setup(
	name='urlget',
	version='0.0.3',
	description='Simple site Scraper',
	author = 'Moon, Heung-sub',
	author_email = 'mhs9089@gmail.com',
	py_modules = ['urlget'],
	install_requires=['requests', 'bs4', 'tqdm'],
)