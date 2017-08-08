# -*- coding: utf-8 -*-
"""reactjo.reactjo: provides entry point main()."""
__version__ = "1.4.0"

import sys
import os
import subprocess

from reactjo.helpers.file_manager import file_manager
from reactjo.helpers.config_manipulation import get_cfg, set_cfg

def update():
	cfg = get_cfg()
	extensions = cfg['extensions']
	for x in extensions:
		path = cfg['paths']['reactjorc'] + '/extensions/' + x['title']
		subprocess.call(['git', 'clone', x['uri'], path])

def initialize():
	if not os.path.exists('reactjorc'):
		os.mkdir('reactjorc')
	if not os.path.exists('reactjorc/extensions'):
		os.mkdir('reactjorc/extensions')
	if not os.path.exists('reactjorc/config.json'):
		file_manager('reactjorc/config.json', 'w', 
			'{"paths": {}, "extensions": []}'
		)
		cfg = get_cfg()
		cfg['paths']['root'] = os.getcwd()
		cfg['paths']['reactjorc'] = os.getcwd() + '/reactjorc'
		default_extension = {
			"title": "react-django",
			"uri": "https://github.com/aaron-price/reactjo-react-django.git"
		}
		cfg['extensions'].append(default_extension)
		set_cfg(cfg)

def main():
	cmd = sys.argv[1]
	if cmd in ['init', 'initialize']:
		initialize()
		update()

	elif cmd in ['update']:
		update()

	else:
		cfg = get_cfg()
		for ext in cfg['extensions']:
			path = cfg['paths']['reactjorc'] + '/extensions/{}/entry.py'.format(
				ext['title']
			)
			subprocess.call(['python', path, cmd])
