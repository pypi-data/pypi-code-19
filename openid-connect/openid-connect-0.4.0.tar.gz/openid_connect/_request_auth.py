from requests.auth import HTTPBasicAuth


class HTTPBearerAuth(object):
	def __init__(self, token):
		self.token = token

	def __eq__(self, other):
		return self.token == getattr(other, 'token', None)

	def __ne__(self, other):
		return not self == other

	def __call__(self, r):
		r.headers['Authorization'] = 'Bearer {}'.format(self.token)
		return r
