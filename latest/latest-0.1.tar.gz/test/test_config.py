import os.path

try:
    import configparser
except:
    import ConfigParser as configparser

import pytest

from latest.util import path


def test_config(config):
    assert config.templates_dir == '~/.latest/templates/'
    assert config.code_entry == '$'
    assert config.code_exit == '$'
    assert config.code_regex == r'\$(?P<code>.*?)\$'
    assert config.ns_operator == '::'
    assert config.block_entry == '<%'
    assert config.block_exit == '%>'
    assert config.inner_block_regex == r'(?P<ns>.*)\:\:(?P<expr>.*)'
    assert config.outer_block_regex == r'\<\%(?P<block>.*?)\%\>'


def test_non_existing_config(non_existing_config):
    assert non_existing_config.code_entry == '{%'
