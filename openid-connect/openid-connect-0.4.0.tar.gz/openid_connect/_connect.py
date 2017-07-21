from importlib import import_module

from six.moves.urllib_parse import unquote, urlsplit, urlunsplit, parse_qs

from ._netloc import make_netloc
from ._oidc import OpenIDClient


def connect_url(url):
	components = urlsplit(url)

	try:
		protocol, scheme = components.scheme.split('+', 1)
	except ValueError:
		protocol = None
	else:
		components = components._replace(scheme=scheme)

	client_id = unquote(components.username) if components.username else None
	client_secret = unquote(components.password) if components.password else None
	components = components._replace(netloc=make_netloc(components.hostname, components.port))

	if not components.path:
		components = components._replace(path='/')

	kwargs = {}
	if components.query:
		kwargs = dict(parse_qs(components.query))
		components = components._replace(query='')

	server = urlunsplit(components)
	return connect(server, client_id, client_secret, protocol, **kwargs)

def connect(server, client_id, client_secret, protocol=None, **kwargs):
	if not protocol:
		cls = OpenIDClient
	else:
		cls = import_module('openid_connect.legacy.' + protocol).Client

	return cls(server, client_id, client_secret, **kwargs)
