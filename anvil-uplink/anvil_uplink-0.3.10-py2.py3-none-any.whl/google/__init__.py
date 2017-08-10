
import anvil, anvil.server

_config = None

def set_client_config(params):
    global _config

    _config = params

def get_config():
	global _config
	if _config is None:
		_config = anvil.server.call("anvil.private.google.get_config")
	return _config
