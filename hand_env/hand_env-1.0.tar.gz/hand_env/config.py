import os
import sys
import json


class HandConfig(object):
    _config = None
    _debug = None
    _argv_prefix = None
    _env_name = None

    def __init__(self, config_file=None, argv_prefix='-json=', env_name='PYTHON_CONFIG_JSON', debug=False):
        self.set_argv_prefix(argv_prefix)
        self.set_env_name(env_name)
        self.set_debug(debug)

        self.init_config(config_file)

    def add_sys_path(self, name):
        path = self.get_config(name)
        if path:
            sys.path.append(path)

    def set_config(self, name, value):
        key_arr = name.split('.')
        value_arr = []

        config = self.get_config()
        for key in key_arr:

            value_arr.append({
                'key': key,
                'value': config
            })

            if type(config) is dict and key in config.keys():
                config = config[key]
                if type(config) is not dict:
                    config = {}
            else:
                config = {}

        for item in reversed(value_arr):
            item['value'][item['key']] = value
            value = item['value']

    def get_config(self, name=None):
        if name is None:
            return self._config
        else:
            value = self.get_config()

            key_arr = name.split('.')
            for key in key_arr:
                if type(value) == dict:
                    value = value.get(key)
                else:
                    return None

            return value

    def load_config(self, config_file):
        if config_file:
            try:
                with open(config_file) as json_file:
                    self._config = json.load(json_file)
            except FileNotFoundError:
                if self._debug:
                    print('file [' + config_file + '] not exist')
            except:
                if self._debug:
                    print('file [' + config_file + '] is not a valid json')

        if self._config is None:
            self._config = {}

    def init_config(self, config_file=None):
        if config_file is None:
            config_file = self.get_config_file_argv()

        if config_file is None:
            config_file = self.get_config_file_env()

        self.load_config(config_file)

    def get_config_file_argv(self):
        config_path = None
        argv_len = len(self._argv_prefix)
        for param in sys.argv:
            if param[0:argv_len] == self._argv_prefix:
                config_path = param[argv_len:]
                break
        return config_path

    def set_argv_prefix(self, argv_prefix):
        self._argv_prefix = argv_prefix

    def get_config_file_env(self):
        return os.environ.get(self._env_name)

    def set_env_name(self, env_name):
        self._env_name = env_name

    def set_debug(self, debug):
        self._debug = debug


hand_config = None


def get_global_config(config_file=None, argv_prefix='-json=', env_name='PYTHON_CONFIG_JSON', debug=False):
    global hand_config
    if hand_config is None:
        hand_config = HandConfig(config_file, argv_prefix, env_name, debug)
    return hand_config
