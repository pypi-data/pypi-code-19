__version__ = '0.1b15'

import functools
import logging
import os
import sys
import shutil
import jinja2

import aiohttp
import aiohttp.web
import aiohttp_security
import aiohttp_session.redis_storage
import aioredis
import aiopg
import aiopg.sa
import sys
import json
import requests_oauthlib
import ssl
import modconf
import argparse
import asyncio
import pickle
import subprocess

import ws_sheets_server

import ws_web_aiohttp.server

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(__file__)

def runserver(args):
    ws_web_aiohttp.server.runserver(args)

def install(args):
    # copy systemd file
    shutil.copyfile(
            os.path.join(BASE_DIR, 'ws_web_aiohttp.service'),
            os.path.join('/lib/systemd/system', 'ws_web_aiohttp.service'))

    config_dir_dst = '/etc/ws_web_aiohttp/conf'

    # make etc directory
    try:
        os.makedirs(config_dir_dst)
    except: pass
    
    # copy default config file
    shutil.copyfile(
            os.path.join(BASE_DIR, 'tests/conf/simple.py'),
            os.path.join(config_dir_dst, 'simple.py'))

    p = subprocess.Popen(('systemctl', 'daemon-reload'))
    p.communicate()
    p = subprocess.Popen(('systemctl', 'restart', 'ws_web_aiohttp.service'))
    p.communicate()

def test_storage(varg):
    from ws_web_aiohttp.tests.test_database import _test
    loop = asyncio.get_event_loop()

    _test(loop, varg['conf_mod'], varg['conf_dir'])
    

def main(argv):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    def help_(args):
        parser.print_help()

    parser.set_defaults(func=help_)
    
    # runserver
    parser_runserver = subparsers.add_parser('runserver')
    parser_runserver.add_argument('--conf_dir')
    parser_runserver.add_argument('conf_mod')
    parser_runserver.add_argument('--dev', action='store_true')
    parser_runserver.add_argument('--console', action='store_true')
    parser_runserver.add_argument('--port', type=int, help='port')
    parser_runserver.add_argument('--addr_compute', help='address of compute server', nargs=2)
    parser_runserver.add_argument('--prefix', help='prefix')
    parser_runserver.add_argument('--test_key', help='test key')
    parser_runserver.set_defaults(func=runserver)

    # install
    parser_install = subparsers.add_parser('install')
    parser_install.set_defaults(func=install)

    # test_storage
    parser_test_storage = subparsers.add_parser('test_storage')
    parser_test_storage.set_defaults(func=test_storage)
    parser_test_storage.add_argument('conf_mod')
    parser_test_storage.add_argument('--conf_dir')

    args = parser.parse_args(argv[1:])
    args.func(vars(args))



if __name__=='__main__':
    main(sys.argv)




