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
				elif option == 'slack_url':
					if isinstance(val, str):
						self.slack_url = val	
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
				# where your node.js server resides
				self.BASE_URL = 'http://52.207.228.129:3001'
				################################################

				self.ENABLED = True
				self.SOUND_ENABLED = False
				self.sound_word = ""
				self.EMAIL_ENABLED = True
				self.emails = []
				self.SLACK_ENABLED = False
				self.slack_url = ""

				self.logtext = "Your code has finished running!"
				self.hasError = False
				
		def options(self):
				return {'on': self.ENABLED, 
								'sound_enabled': self.SOUND_ENABLED, 'sound_word': self.sound_word,
								'email_enabled': self.EMAIL_ENABLED, 'emails': self.emails, 
								'slack_enabled': self.SLACK_ENABLED, 'slack_url': self.slack_url,
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
				if 'slack_url' in options:
					self.slack_url = options['slack_url']
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
						except: # Windows (Might not work if terminal bell is disabled)
								print('\a')

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
					if len(self.slack_url) == 0:
						print('Please enter your Slack url for ping. You may obtain it from https://my.slack.com/services/new/incoming-webhook/')
						return
					payload = {'text': logtext_to_use, 'username': 'CodeAlert', 'icon_emoji': ':tada:'}
					headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
					response = requests.post(self.slack_url, headers=headers, data=json.dumps(payload))
		 
# Ping decorator
def pingd(calert, options):
		import copy
		_calert = copy.copy(calert)
		_calert.set_options(options)
		def ping_decorator(func):
				def func_wrapper(*args, **kwargs):
						try:
								# Capture all print statements and forward them to ping
								import sys
								try:
										from StringIO import StringIO
								except ImportError:
										from io import StringIO
								
								stdout_ = sys.stdout # Keep track of the previous stdout
								stream = StringIO()
								sys.stdout = stream

								func(*args, **kwargs) # Execute function here while capturing stdout

								sys.stdout = stdout_ # Restore the previous stdout
								print_statements = stream.getvalue()
								_calert.ping(print_statements)
						except Exception as e:
								_calert.hasError = True
								_calert.ping('Error: ' + str(e))
				return func_wrapper
		return ping_decorator
