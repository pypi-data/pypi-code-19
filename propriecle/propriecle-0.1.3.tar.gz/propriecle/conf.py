"""All dat conf"""

import os
import yaml
from propriecle.helpers import problems


def config_file():
    """Returns the config file or a potentially sane default"""
    if 'PROPRIECLE_CONFIG' in os.environ:
        return os.environ['PROPRIECLE_CONFIG']

    return "%s/.proprieclerc" % os.environ['HOME']


class PropriecleConfig(object):
    """A class representing the runtime configuration"""
    config = {}

    def __init__(self):
        filename = config_file()
        if os.path.exists(filename):
            self.config = yaml.safe_load(open(filename).read())
        else:
            problems("No config file found")

    def get(self, key, default):
        return self.config.get(key, default)

MY_CONFIG = PropriecleConfig()


def get(key, default=None):
    """Return a config entry, or the default if nothing explicitly
    set has been found"""
    return MY_CONFIG.get(key, default)


def state_directory():
    """Return the state directory. This is used for saving encrypted keys."""
    prefix = "%s/.propriecle" % os.environ['HOME']
    if 'PROPRIECLE_DIRECTORY' in os.environ:
        prefix = os.environ['PROPRIECLE_DIRECTORY']

    return prefix


def get_server(name):
    """Returns the basic configuration expression of
    a Vault server. This is the basis for the full expression of
    the server but lacks details."""
    if isinstance(name, dict):
        return get_server(name['name'])

    vaults = get('vaults')
    for s in vaults:
        if name == s['name']:
            return s

    problems("Invalid Vault")
