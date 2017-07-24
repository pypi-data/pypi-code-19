from aiohttp import request

from .data import PlecostOptions


def check_xmlrpc(config):
    assert isinstance(config, PlecostOptions)

