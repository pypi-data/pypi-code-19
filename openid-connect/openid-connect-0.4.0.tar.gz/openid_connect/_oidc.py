import requests
from jose import jwt

from six.moves.urllib_parse import urlencode

from ._property import overwritable_property
from ._request_auth import HTTPBasicAuth, HTTPBearerAuth


class TokenResponse(object):
	def __init__(self, data, client=None):
		self._data = data
		self._client = client

	@property
	def access_token(self):
		return self._data["access_token"]

	@property
	def id_token(self):
		return self._data["id_token"]

	@property
	def userinfo(self):
		try:
			return self._userinfo
		except AttributeError:
			userinfo = self._client.get_userinfo(self.access_token)
			if self.id["sub"] != userinfo["sub"]:
				return None
			self._userinfo = userinfo
			return self._userinfo

class OpenIDClient(object):
	def __init__(self, url, client_id=None, client_secret=None, initial_auth=None, initial_access_token=None, registration_client_uri=None, registration_auth=None, registration_access_token=None):
		self.url = url
		self.client_id = client_id
		self.client_secret = client_secret

		if initial_auth:
			self.initial_auth = initial_auth
		self.initial_access_token = initial_access_token

		self.registration_client_uri = registration_client_uri
		if registration_auth:
			self.registration_auth = registration_auth
		self.registration_access_token = registration_access_token

		self._configuration = self.get_configuration()

	@overwritable_property
	def auth(self):
		if self.client_secret:
			return HTTPBasicAuth(self.client_id, self.client_secret)
		else:
			return None

	def get_configuration(self):
		r = requests.get(self.url + ".well-known/openid-configuration")
		r.raise_for_status()
		return r.json()

	def translate_scope_in(self, scope):
		return scope

	def translate_scope_out(self, scope):
		return scope

	def translate_userinfo(self, userinfo):
		return userinfo

	def get_id(self, token_response):
		return jwt.decode(
			token_response.id_token,
			self.keys,
			algorithms = ['RS256'],
			audience = self.client_id,
			issuer = self.issuer,
			options = dict(verify_at_hash = False),
		)

	@property
	def issuer(self):
		return self._configuration["issuer"]

	@property
	def authorization_endpoint(self):
		return self._configuration["authorization_endpoint"]

	@property
	def token_endpoint(self):
		return self._configuration["token_endpoint"]

	@property
	def jwks_uri(self):
		return self._configuration["jwks_uri"]

	@property
	def userinfo_endpoint(self):
		return self._configuration["userinfo_endpoint"]

	@property
	def end_session_endpoint(self):
		return self._configuration.get("end_session_endpoint")

	@property
	def registration_endpoint(self):
		return self._configuration.get("registration_endpoint")

	@property
	def keys(self):
		r = requests.get(self._configuration["jwks_uri"])
		r.raise_for_status()
		return r.content.decode('utf-8')

	def get_userinfo(self, access_token):
		r = requests.get(self.userinfo_endpoint, headers=dict(
			Authorization = "Bearer " + access_token,
		))
		r.raise_for_status()
		data = r.json()
		return self.translate_userinfo(data)

	def authorize(self, redirect_uri, state='', scope=('openid',)):
		scope = set(self.translate_scope_in(scope))
		return self.authorization_endpoint + "?" + urlencode(dict(
			client_id=self.client_id,
			response_type="code",
			redirect_uri=redirect_uri,
			state=state,
			scope=" ".join(scope),
		))

	def request_token(self, redirect_uri, code):
		r = requests.post(self.token_endpoint, auth=self.auth, data=dict(
			grant_type="authorization_code",
			redirect_uri=redirect_uri,
			code=code,
		), headers={'Accept': 'application/json'})
		r.raise_for_status()
		resp = TokenResponse(r.json(), self)

		if "scope" in resp._data:
			resp.scope = set(self.translate_scope_out(set(resp._data["scope"].split(" "))))
		if not hasattr(resp, "scope") or "openid" in resp.scope:
			resp.id = self.get_id(resp)

		return resp

	def end_session(self, post_logout_redirect_uri, state, id_token_hint=''):
		if not self.end_session_endpoint:
			raise NotImplementedError("This OP does not support RP-initiated logout.")

		return self.end_session_endpoint + "?" + urlencode(dict(
			post_logout_redirect_uri=post_logout_redirect_uri,
			state=state,
			id_token_hint=id_token_hint,
		))

	@overwritable_property
	def initial_auth(self):
		if self.initial_access_token:
			return HTTPBearerAuth(self.initial_access_token)
		else:
			# TODO? Write an OAuth extension for using Basic auth for registration_endpoint.
			return self.auth

	def register(self, auth=None, access_token=None, **client_config):
		if not self.registration_endpoint:
			raise NotImplementedError("This OP does not support Dynamic Client Registration.")

		if not auth and access_token:
			auth = HTTPBearerAuth(access_token)

		if not auth:
			auth = self.initial_auth

		r = requests.post(self.registration_endpoint, auth=auth, json=client_config)
		r.raise_for_status()
		data = r.json()
		client = type(self)(self.url, client_id=data['client_id'], client_secret=data.get('client_secret'), registration_client_uri=data.get('registration_client_uri'), registration_access_token=data.get('registration_access_token'))
		return client, data

	@overwritable_property
	def registration_auth(self):
		if self.registration_access_token:
			return HTTPBearerAuth(self.registration_access_token)
		else:
			# TODO Write an OAuth extension for using normal auth for registration_client_uri.
			return self.auth

	@property
	def client(self):
		if not self.registration_client_uri:
			raise NotImplementedError("registration_client_uri was not provided.")

		r = requests.get(self.registration_client_uri, auth=self.registration_auth)
		r.raise_for_status()
		return r.json()

	@client.setter
	def client(self, config):
		if not self.registration_client_uri:
			raise NotImplementedError("registration_client_uri was not provided.")

		r = requests.put(self.registration_client_uri, auth=self.registration_auth, json=config)
		r.raise_for_status()
		return r.json()

	@client.deleter
	def client(self):
		if not self.registration_client_uri:
			raise NotImplementedError("registration_client_uri was not provided.")

		r = requests.delete(self.registration_client_uri, auth=self.registration_auth)
		r.raise_for_status()
