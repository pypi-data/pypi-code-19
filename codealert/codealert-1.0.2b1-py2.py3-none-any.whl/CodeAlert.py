class CodeAlert:
		
	# Used for method chaining
	def set(self, option, val):
		if option == 'sound_enabled':
			if isinstance(val, bool):
				self.SOUND_ENABLED = val
			elif isinstance(val, str):
				self.SOUND_ENABLED = True
				self.sound_word = val
		elif option == 'email_enabled':
			if isinstance(val, bool):
				self.EMAIL_ENABLED = val
		elif option == 'emails':
			if isinstance(val, list):
				for v in val:
					if not isinstance(v, str):
						return self
				self.emails = val
		elif option == 'slack_enabled':
			if isinstance(val, bool):
				self.SLACK_ENABLED = val
		elif option == 'slack_urls':
			if isinstance(val, list):
				for v in val:
					if not isinstance(v, str):
						return self
				self.slack_urls = val	
		elif option == 'on':
			if isinstance(val, bool):
				self.ENABLED = val
		elif option == 'logtext':
			if isinstance(val, str):
				self.logtext = val
		return self
			
	def __init__(self):
		################################################
		# Change this to your self hosted server IP, 
		# where your node.js server resides. 
		# A node server is only needed if you require 
		# email functionality.
		self.BASE_URL = 'http://52.207.228.129:3001'
		################################################

		self.ENABLED = True
		self.SOUND_ENABLED = True
		self.sound_word = ""
		self.EMAIL_ENABLED = False
		self.emails = []
		self.SLACK_ENABLED = False
		self.slack_urls = []

		self.logtext = "Your code has finished running!"
		self.hasError = False
			
	def options(self):
		return {'on': self.ENABLED, 
						'sound_enabled': self.SOUND_ENABLED, 'sound_word': self.sound_word,
						'email_enabled': self.EMAIL_ENABLED, 'emails': self.emails, 
						'slack_enabled': self.SLACK_ENABLED, 'slack_urls': self.slack_urls,
						'logtext': self.logtext}
	
	def set_options(self, options):
		if 'on' in options:
			self.ENABLED = options['on']
		if 'sound_enabled' in options:
			val = options['sound_enabled']
			if isinstance(val, bool):
				self.SOUND_ENABLED = val
			elif isinstance(val, str):
				self.SOUND_ENABLED = True
				self.sound_word = val
		if 'email_enabled' in options:
			self.EMAIL_ENABLED = options['email_enabled']
		if 'emails' in options:
			self.emails = options['emails']
		if 'slack_enabled' in options:
			self.SLACK_ENABLED = options['slack_enabled']
		if 'slack_urls' in options:
			self.slack_urls = options['slack_urls']
		if 'logtext' in options:
			self.logtext = options['logtext']
	
	def ping(self, logtxt=""):
		import os
		import requests
		import json
		
		if not self.ENABLED:
			return

		if self.SOUND_ENABLED:
			try: # Mac
				if self.hasError: 
					os.system('say "error"')
				elif self.sound_word:
					os.system('say "' + self.sound_word + '"')
				else:
					os.system('afplay /System/Library/Sounds/Glass.aiff')
			except: # Windows (Might not work if command prompt bell is disabled)
				print('\a')

		# Logging priority: If there is logtxt > print statements > logtext
		logtext_to_use = self.logtext if not logtxt else logtxt

		if self.EMAIL_ENABLED:
			if len(self.emails) == 0:
				print('Please enter recipient emails for ping')
				return
			email_url = 'email'
			final_url="{0}/{1}".format(self.BASE_URL, email_url)
			for email in self.emails:
				payload = {'email': email, 'logtext': logtext_to_use}
				headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
				response = requests.post(final_url, headers=headers, data=json.dumps(payload))

		if self.SLACK_ENABLED:
			if len(self.slack_urls) == 0:
				print('Please enter your Slack url for ping. You may obtain it from https://my.slack.com/services/new/incoming-webhook/')
				return
			for slack_url in self.slack_urls:
				payload = {'text': logtext_to_use, 'username': 'CodeAlert', 'icon_emoji': ':tada:'}
				headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
				response = requests.post(slack_url, headers=headers, data=json.dumps(payload))
		 
# Ping decorator
def pingd(calert=CodeAlert(), options={}):
	import copy
	import sys
	try:
		from StringIO import StringIO
	except ImportError:
		from io import StringIO
	_calert = copy.copy(calert)
	_calert.set_options(options)
	def ping_decorator(func):
		def func_wrapper(*args, **kwargs):
			logtext_to_use = ''
			# Capture all print statements and forward them to ping
			stdout_ = sys.stdout # Keep track of the previous stdout
			stream = StringIO()
			sys.stdout = stream

			try:
				func(*args, **kwargs) # Execute function here while capturing stdout
			except Exception as e:
				_calert.hasError = True
				logtext_to_use = 'Error:\n======\n' + str(e) + '\n\n'
				# _calert.ping(logtext_to_use + '\nError: ' + str(e))

			sys.stdout = stdout_ # Restore the previous stdout
			print_statements = stream.getvalue()
			logtext_to_use += 'Print:\n======\n' + print_statements

			_calert.ping(logtext_to_use)

		return func_wrapper
	return ping_decorator
