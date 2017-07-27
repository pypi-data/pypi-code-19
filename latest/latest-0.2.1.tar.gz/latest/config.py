""":mod:`config` module contains configuration functions and classes for :mod:`latest` package.

:mod:`latest` is completely customizable in its syntax both programmatically and through a configuration file.

Configurations are contained in an object of the class :class:`_Config` that take an optional keyword argument in his :code:`__init__` method to specify the location of the configuration file. If no configuration file is specified, defaults are set in code. The default configuration object :code:`config` is defined in this module and can be imported to be used elsewhere. I suggest an import statement like

.. code::

    from latest.config import config as Config

Then, you can think of the configuration object as a class with many static methods. To create an alternate configuration object you can use the public function :code:`create_config(config_file=None)` instead of directly instantiate an object of private class :class:`_Config`.

Configuration file is found by default (default configuration object look for this location) in :code:`~/.latest/latest.cfg` but one can use his own configuration file. Configuration files must be in :code:`ini` format. Useful sections are:

    * **general**
    * **lang**

The section *lang* of the configuration file is where one can define its own syntax. Available options in `lang` section are:

    * `cmd_entry`
    * `cmd_exit`
    * `env_entry`
    * `env_exit`
    * `ns_operator`


"""

import os
import re

try:
    import configparser
except:
    import ConfigParser as configparser

import latest
from .util import path, getopt


_BASE_DIR = path('~/.' + latest.__project__ + '/')
_CONFIG_FILE = os.path.join(_BASE_DIR, latest.__project__ + 'cfg')
_TEMPLATES_DIR = os.path.join(_BASE_DIR, 'templates/')


class _Config(object):


    _OPTIONS = (
        # section, key, default
        ('general', 'templates_dir', _TEMPLATES_DIR),
        ('general', 'default_data_fmt', 'json'),
        ('general', 'join_items', str()),
        ('lang', 'opt_regex', r'\s*(?P<key>[^,=]*?)\s*=\s*\{(?P<value>.*?)\}\s*'),
        ('lang', 'cmd_entry', r'\\latest(\[(?P<opts>.*?)\])?\{\$'),
        ('lang', 'cmd_exit', r'\$\}'),
        ('lang', 'env_entry', r'\\begin\{latest\}\{(?P<ns>.*?)\}(\[(?P<opts>.*?)\])?\s?'),
        ('lang', 'env_exit', r'\s?\\end\{latest\}'),
        ('lang', 'ns_operator', r'.'),
    )

    CMD_CONTENT_TAG = 'code'
    ENV_CONTENT_TAG = 'expr'
    OPT_TAG = 'opts'
    OPT_KEY_TAG = 'key'
    OPT_VALUE_TAG = 'value'
    NS_TAG = 'ns'


    def __init__(self, config_file=None):
        if config_file:
            self.read(config_file)
        else:
            self.set_defaults()


    def set_defaults(self):
        for section, key, default in self._OPTIONS:
            setattr(self, key, default)


    def read(self, filename):

        config_file = path(filename)
        if not hasattr(self, 'config_files'):
            self.config_files = list()
        self.config_files.append(config_file)

        parser = configparser.RawConfigParser()
        parser.read(config_file)
        for section, key, default in self._OPTIONS:
            value = getopt(parser, section, key, default)
            setattr(self, key, value)


    @property
    def cmd_regex(self):
        return self.cmd_entry + r'(?P<' + self.CMD_CONTENT_TAG + r'>.*?)' + self.cmd_exit


    @property
    def env_regex(self):
        return self.env_entry + r'(?P<' + self.ENV_CONTENT_TAG + r'>[\s\S]*?)' + self.env_exit



def create_config(config_file=None):
    return _Config(config_file)


config = _Config(config_file=_CONFIG_FILE)


