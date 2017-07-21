""":mod:`config` module contains configuration functions and classes for :mod:`latest` package.

:mod:`latest` is completely customizable even in its syntax.

Configuration file is found by default in `~/.latest/latest.cfg` but one can use his configuration objects/files.

The section `lang` of the configuration file is where one can define its own syntax.

Available options in `lang` section are:

    * `code_entry`
    * `code_exit`
    * `ns_operator`
    * `block_entry`
    * `block_exit`


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
        ('general', 'join_items', os.linesep),
        ('lang', 'code_entry', '{%'),
        ('lang', 'code_exit', '%}'),
        ('lang', 'ns_operator', '::'),
        ('lang', 'block_entry', '<<<'),
        ('lang', 'block_exit', '>>>'),
    )

    _CODE_TAG = 'code'
    _NS_TAG = 'ns'
    _EXPR_TAG = 'expr'
    _BLOCK_TAG = 'block'


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
    def code_regex(self):
        return re.escape(self.code_entry) + r'(?P<code>.*?)' + re.escape(self.code_exit)


    @property
    def inner_block_regex(self):
        return r'(?P<ns>.*)' + re.escape(self.ns_operator) + '(?P<expr>.*)'


    @property
    def outer_block_regex(self):
        return re.escape(self.block_entry) + r'(?P<block>.*?)' + re.escape(self.block_exit)



def create_config(config_file=None):
    return _Config(config_file)


config = _Config(config_file=_CONFIG_FILE)


