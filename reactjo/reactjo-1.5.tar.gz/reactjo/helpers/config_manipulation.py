import subprocess
import os
import json
from reactjo.helpers.file_manager import json_read, json_write

def find_config_path():
	def check():
		# reactjo.json exists?
		config_file = os.path.isfile('./reactjorc/config.json')
		if config_file:
			return found()
		else:
			return bubble_up(os.getcwd())

	def bubble_up(prev_path):
		os.chdir("..")
		next_path = os.getcwd()
		if prev_path == next_path:
			# Escape the recursion if "cd .." does nothing.
			return failure()
		else:
			return check()
	
	def found():
		return os.getcwd() + '/reactjorc/config.json'

	def failure():
		print("Sorry, couldn't find the config.json file. cd to that directory, or a child directory.")
		print("""If there really is no config.json, you probably need to create a project. Try running:
		----------------------
		reactjo init
		----------------------
		""")

	return check()

def get_cfg():
	return json_read(find_config_path())

def set_cfg(content):
	json_write(find_config_path(), content)