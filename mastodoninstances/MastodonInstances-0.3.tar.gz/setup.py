#!/usr/bin/env python3
from setuptools import setup

setup(name='MastodonInstances',
	version='0.3',
	description='Python Interface to instances.social',
	author='Thomas "Cakeisalie5" Touhey',
	author_email='thomas@touhey.fr',
	url='https://github.com/cakeisalie5/MastodonInstances',
	keywords='mastodon instances instances.social api microblogging',

	scripts=['scripts/mastodon-instances'],
	packages=['MastodonInstances'],
	install_requires=['requests', 'bs4', 'html5lib'],

	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 3'
	]
)

# End of file.
