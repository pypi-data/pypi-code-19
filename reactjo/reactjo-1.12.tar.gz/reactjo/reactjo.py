# -*- coding: utf-8 -*-
"""reactjo.reactjo: provides entry point main()."""
__version__ = "1.0.0"

import sys
import os
import subprocess
import shutil
from reactjo.helpers.file_manager import file_manager
from reactjo.helpers.config_manipulation import get_cfg, set_cfg

def update():
	cfg = get_cfg()
	extensions = cfg['paths']['reactjorc'] + '/extensions/'

	if os.path.exists(extensions):
		shutil.rmtree(extensions)
	os.mkdir(extensions)

	for x in cfg['extensions']:
		path = extensions + x['title']
		
		if 'branch' in x:
			subprocess.call(['git', 'clone', '-b', x['branch'], x['uri'], path])
		else:
			subprocess.call(['git', 'clone', x['uri'], path])
		
		dependencies = path + '/requirements.txt'
		if os.path.exists(dependencies):
			deps = file_manager(dependencies, 'r')
			if len(deps) > 0:
				subprocess.call(['pip', 'install', '-r', dependencies])


def extend():
	src = 'https://github.com/aaron-price/reactjo-extension-template.git'
	target = os.getcwd()
	subprocess.call([ 'git', 'clone', src, target + '/template' ])

def print_worklist():
	cfg = get_cfg()
	if 'worklist' in cfg:
		wl = cfg['worklist']
		if len(wl) > 0:
			print(" ")
			print("Here's what Reactjo just did for you")
			for item in wl:
				print(item)

		print("Enjoy :-)")
		print(" ")

		cfg['worklist'] = []
		set_cfg(cfg)

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
		cfg['paths']['super_root'] = os.getcwd()
		cfg['paths']['reactjorc'] = os.getcwd() + '/reactjorc'
		default_extension = {
			"title": "react-django",
			"uri": "https://github.com/aaron-price/reactjo-react-django.git"
		}
		cfg['extensions'].append(default_extension)
		set_cfg(cfg)

def main():
	cmd = sys.argv[1]
	if cmd in ['init', 'initialize', 'i']:
		initialize()
		update()

	elif cmd in ['update', 'u']:
		update()
	elif cmd in ['extend', 'extension', 'e']:
		extend()

	else:
		cfg = get_cfg()
		for ext in cfg['extensions']:
			path = cfg['paths']['reactjorc'] + '/extensions/{}/entry.py'.format(
				ext['title']
			)
			subprocess.call(['python', path, cmd])

		print_worklist()