
import functools
import os
import sys
import shutil

import sys
import json
import argparse
import asyncio
import pickle
import base64
import subprocess

import async_patterns.protocol
import modconf.remote

import pytest

class ServerClientProtocol(async_patterns.protocol.Protocol):
    def __init__(self, loop, app):
        super(ServerClientProtocol, self).__init__(loop)
        self.app = app
        self.config_manager = app.config_manager

class ConfigManager:
    def __init__(self):
        self.__configs = {}
    def register(self, id_, c):
        self.__configs[id_] = c
    def get(self, id_):
        return self.__configs.get(id_, None)

class App: pass

@pytest.fixture
async def server_addr(event_loop):
    print()

    app = App()

    coro = event_loop.create_server(
            functools.partial(ServerClientProtocol, event_loop, app),
            'localhost', 
            0)
    
    server = await coro

    app.config_manager = ConfigManager()
    app.config_manager.register('import_class', modconf.import_class)
    
    addr = server.sockets[0].getsockname()
    port = addr[1]

    print('serving on', addr)
    
    yield addr
    
    server.close()
    await server.wait_closed()

@pytest.mark.asyncio
async def test(event_loop, server_addr):
    
    c = await modconf.remote.import_class(
            event_loop,
            server_addr[0],
            server_addr[1],
            'import_class',
            'modconf.tests.conf.conf_class',
            'Conf',
            tuple(),
            {})

    print(c)



