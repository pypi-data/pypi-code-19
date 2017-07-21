from six.moves.urllib_parse import quote


def make_netloc(host, port=None, username=None, password=None):
	netloc = ''

	if username:
		netloc = quote(username)
	if password:
		netloc += ':' + quote(password)

	if netloc:
		netloc += '@'

	if ':' in host:
		netloc += '[' + host + ']'  # IPv6 literal
	else:
		netloc += host
	if port:
		netloc += ':' + str(port)

	return netloc
