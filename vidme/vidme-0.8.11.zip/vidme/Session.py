
# import readline
import api
import socket
import sys
import base64
import webbrowser

class Session:

	def __init__(self, settings, no_output = False):
		self.no_output = no_output

		self.oauth = False
		self.auth = False
		self.user = False
		self.oauthing = False
		self.scope = []

		if 'oauth' in settings:
			self.oauth = True
			secret = ""

			if 'key' in settings['oauth'] and settings['oauth']['key']:
				if 'secret' in settings['oauth']:
					secret = settings["oauth"]['secret']

				self.set_oauth(settings["oauth"]['key'], secret)

			if 'client_id' in settings['oauth']:
				self.client_id = settings['oauth']['client_id']
			else:
				self.client_id = ''

			if 'redirect_uri' in settings['oauth']:
				self.redirect_uri = settings['oauth']['redirect_uri']

				if self.redirect_uri != "http://localhost:5010":
					print "[!] Please make sure oauth redirect is: 'http://localhost:5010'"
			else:
				self.redirect_uri = 'http://localhost:5010'

			if 'scope' in settings['oauth'] and settings['oauth']['scope']:
				self.scope = ','.join(settings['oauth']['scope'])
			else:
				self.scope = ''

		if 'username' in settings and settings['username']:
			self.username = settings['username']
		else:
			self.username = None

		if 'password' in settings and settings['password']:
			self.password = settings['password']
		else:
			self.password = None

		if 'code' in settings:
			self.run_oauth(settings['code'])

		if 'token' in settings and settings['token']:
			self.token = settings['token']
			self.auth = True

	def get_auth(self):
		return self.auth

	def get_token(self):
		if self.oauthing:
			return False
		elif self.get_auth():
			return self.token
		else:
			if self.new_token():
				return self.token
			else:
				return None

	def get_user(self):
		return self.user

	def set_oauth(self, key, secret = ""):
		self.key = key
		self.secret = secret
		self.oauth = True

	def get_oauth(self):
		if self.oauth:
			return "Basic " + base64.b64encode(self.key + ":" + self.secret)
		else:
			return False

	def run_oauth(self, code=None):
		if not code:
			link = 'https://vid.me/oauth/authorize?' + \
				'scope=' + self.scope + '&' + \
				'client_id=' + self.client_id + '&' + \
				'response_type=code&' + \
				'redirect_uri=' + self.redirect_uri + '&' + \
				'authorization=allow'

			print "[!] Please visit the following URL:"
			print ""
			print link
			print ""
			 
			HOST = ''   # Symbolic name, meaning all available interfaces
			PORT = 5010 # Arbitrary non-privileged port
			 
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			#Bind socket to local host and port
			try:
			    s.bind((HOST, PORT))
			except socket.error as msg:
			    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			    sys.exit()

			#Start listening on socket
			s.listen(1)

			webbrowser.open_new(link)

			#wait to accept a connection - blocking call
			conn, addr = s.accept()

			code = conn.recv(4096).splitlines()[0].split()[1].split('code=')[1]

			send_back_packet = """HTTP/1.0 200 OK
Content-Type: text/html

Thank you! You are good to go!
"""

			conn.sendall(send_back_packet)
			conn.close()

			s.close()

		self.oauthing = True

		r = api.request('/oauth/token', self, method='POST', params=dict(
			grant_type='client_credentials',
			code=code,
		))

		self.oauthing = False

		return r

	def new_token(self):
		if not self.no_output:
			print '[-] Your token is invalid or has expired!'

		if self.oauth:
			request = self.run_oauth()
		else:
			if not self.username:
				username = raw_input("Please enter your username: ")
			else:
				username = self.username

			if not self.password:
				password = raw_input("Please enter your password: ")
			else:
				password = self.password

			request = api.request('/auth/create', data=dict(
				username=username,
				password=password,
				Authorization="Basic"
			))

		if request:
			from User import User

			self.token = request['auth']['token']
			self.expires = request['auth']['expires']
			self.user = User({'user': request['user']})

			self.auth = True
			return True
		else:
			return False
