import json
from datetime import datetime, timedelta

from consul import Consul

__all__ = ['Config']

class Config(object):
    """A class for fetching configuration values from Consul.
    Overrides may be specified in the form of a JSON file path.
    """
    def __init__(self, consul_host, token, root_key=None, override_file=None, port=80, ttl=timedelta(hours=1)):
        """Constructor for a Config object. Initializes the config object.

        Values can be cached for a certain amount of time so that heavy users are not
        continuously making requests to Consul. By default, values are cached for one hour.

        Args:
            consul_host (required): The host for the Consul KV store.
            root_key (default=''): A string specifying the root key prefix
                                   to use when reading from Consul. By default,
                                   everything will be loaded unless this is specified.
            override_file (default=None): A string path specifying a JSON override
                                          file to load. This file can be used to
                                          override shared configuration values for
                                          development purposes. If this is None then
                                          no override will be loaded.
            port (default=80): The port to use when connecting to Consul.
            token: The Consul token to use when connecting to Consul.
            ttl (default=timedelta<hours=1>): The amount of time to cache config values.
                                              This does not apply to overrides.
        """
        self.consul = Consul(host=consul_host, port=port, token=token)
        self.overrides = {}
        self.last_loaded = {}
        self.cache = {}
        self.ttl = ttl
        self.root_key = root_key

        if override_file is None:
            return

        with open(override_file) as f:
            lines = f.readlines()
            override_data = json.loads(''.join(lines))
            override_data = __flatten__(override_data)
            self.overrides.update(override_data)

    def get_string(self, *args):
        """Returns a configuration string given a variadic list of key paths.

        Returns:
            A string value for the given key. None is returned if the key does
            not exist.
        """
        key = '/'.join(args)

        if self.root_key is not None:
            key = '{}/{}'.format(self.root_key, key)

        now = datetime.utcnow()

        if key in self.overrides:
            return self.overrides.get(key)

        if key in self.last_loaded:
            if self.last_loaded[key] + self.ttl > now:
                return self.cache.get(key)

        self.last_loaded[key] = now

        _, data = self.consul.kv.get(key)

        if data is not None and 'Value' in data:
            value = data['Value'].decode('utf-8')
        else:
            value = None

        self.cache[key] = value

        return value

    def get_integer(self, *args):
        """Returns a configuration integer given a variadic list of key paths.

        Returns:
            An integer value for the given key. None is returned if the key does
            not exist.
        Raises:
            ValueError: Raised in the event that the specified key is not an integer.
        """
        value = self.get_string(*args)

        if value is None:
            return None

        return int(value)

    def get_float(self, *args):
        """Returns a configuration float given a variadic list of key paths.

        Returns:
            An float value for the given key. None is returned if the key does
            not exist.
        Raises:
            ValueError: Raised in the event that the specified key is not a float.
        """
        value = self.get_string(*args)

        if value is None:
            return None

        return float(value)

    def get_boolean(self, *args):
        """Returns a configuration integer given a variadic list of key paths.

        Booleans are defined to be either "true" or "false" in either uppercase,
        lowercase, or mixed-case.

        Returns:
            An boolean value for the given key. None is returned if the key does
            not exist.
        Raises:
            ValueError: Raised in the event that the specified key is not a boolean.
        """
        value = self.get_string(*args)

        if value is None:
            return None

        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        else:
            raise ValueError(
                'Unable to parse boolean from string value: {}. Valid values are true and false.'.format(value)
            )

def __flatten__(json_dict):
    flattened_dict = {}

    def flatten(key, val):
        if isinstance(val, dict):
            for k, v in val.items():
                new_key = k if key is None else '{}/{}'.format(key, k)
                flatten(new_key, v)
        else:
            flattened_dict[key] = val

    flatten(None, json_dict)

    return flattened_dict

def __format_key__(key_parts):
    return '/'.join(key_parts)
