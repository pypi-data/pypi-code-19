__version__ = '0.4.1b21'

import argparse
import json
import logging
import logging.config
import os
import sys
import shutil
import subprocess

import ws_sheets_server.server_aio

BASE_DIR = os.path.dirname(__file__)

class Cell(object):
    def __init__(self, string, value):
        self.string = string
        self.value = value

class Server(object):
    """
    This class is an abstaction for sending and
    receiving book data to and from a BookProxy object.
    The purpose of the Server is to keep
    Book objects loaded in memory.
    """
    def __init__(self, storage):
        """
        :param storage: a Storage object
        """
        self.storage = storage

    def get_book(self, book_id):
        return self.storage.get_object(book_id)

    def save_book(self, book_id):
        return self.storage.save_object(book_id)

class BookProxy(object):
    """
    This class is an abstraction for indirect access to a Book object.
    Implementations shall define all the methods of Book that a client needs.
    """
    pass

def install(args):
    # copy systemd file
    shutil.copyfile(
            os.path.join(BASE_DIR, 'ws_sheets_server.service'),
            os.path.join('/lib/systemd/system', 'ws_sheets_server.service'))

    config_dir_dst = '/etc/ws_sheets_server/conf'

    # make etc directory
    try:
        os.makedirs(config_dir_dst)
    except: pass
    
    # copy default config file
    shutil.copyfile(
            os.path.join(BASE_DIR, 'tests/conf/simple.py'),
            os.path.join(config_dir_dst, 'simple.py'))
    shutil.copyfile(
            os.path.join(BASE_DIR, 'tests/conf/simple_console.py'),
            os.path.join(config_dir_dst, 'simple_console.py'))

    p = subprocess.Popen(('systemctl', 'daemon-reload'))
    p.communicate()
    p = subprocess.Popen(('systemctl', 'restart', 'ws_sheets_server.service'))
    p.communicate()

def runserver(args):
    ws_sheets_server.server_aio.runserver(args)

def test_storage(args):
    from ws_sheets_server.tests.check_stored import TestCheckStored
    test_case = TestCheckStored()
    test_case.conf_dir = args.conf_dir
    test_case.conf_mod = args.conf_mod
    test_case.d = args.d
    
    try:
        test_case.test()
    except Exception as e:
        print('Fail')
        print(e)
        sys.exit(1)
    else:
        sys.exit(0)

def main(argv):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    def help_(args):
        parser.print_help()
   
    parser.set_defaults(func=help_)
    
    # runserver
    parser_runserver = subparsers.add_parser('runserver')
    parser_runserver.add_argument(
            '--conf_dir',
            help='modconf module directory',
            )
    parser_runserver.add_argument(
            'conf_mod',
            help='modconf module name',
            )
    parser_runserver.add_argument(
            '-d',
            action='store_true',
            help='development mode')
    parser_runserver.set_defaults(func=runserver)
 
    # test_storage
    parser_runserver = subparsers.add_parser('test_storage')
    parser_runserver.add_argument(
            '--conf_dir',
            help='modconf module directory',
            )
    parser_runserver.add_argument(
            'conf_mod',
            help='modconf module name',
            )
    parser_runserver.add_argument(
            '-d',
            action='store_true',
            help='development mode')
    parser_runserver.set_defaults(func=test_storage)
 
    # install
    parser_install = subparsers.add_parser('install')
    parser_install.set_defaults(func=install)

    args = parser.parse_args(argv[1:])
    args.func(vars(args))


