"""
This file contains a CypressBase class. Inherit
"""
import os
from .logger_helper import get_logger


class CypressBase(object):

    def __init__(self):
        self.debug_mode = self.__is_debug_mode()
        self.logger = get_logger(__name__, verbose=self.is_verbose())

    def get_debug_mode(self):
        return self.debug_mode

    def __is_debug_mode(self):
        return self.get_value_from_env('DEBUG', default=False)

    def is_verbose(self):
        return self.debug_mode or self.get_value_from_env('VERBOSE', default=False)

    def get_value_from_env(self, key, default=None):
        """
        This method reads the value from the environment by the name of `key`. If the variable is not set, it returns the `default` value.
        :param key: the environment variable name.
        :param default: default value if the variable is not set.
        :return: the value or a default value of an environment variable represented by the key
        """
        val = default
        try:
            v = os.environ.get(key)
            if v.lower() == 'true':
                val = True
            elif v.lower() == 'false':
                val = False
            else:   # convert the value to the `default` type
                val_type = str if default is None else type(default)
                val = val_type(v)
        except AttributeError:
            pass

        return val
