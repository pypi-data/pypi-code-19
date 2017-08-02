#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import socket
from ConfigParser import ConfigParser
import ujson


class Config(dict):

    def __init__(self):
        dict.__init__(self, {})
        self.root_path = os.getcwd()
        self['g_ip'] = socket.gethostname()

    def from_ini(self, file_name):
        config_path = os.path.join(self.root_path, file_name)
        assert os.path.isfile(config_path), '缺少 %s 文件' % file_name
        cf = ConfigParser()
        cf.read(config_path)
        config_type = cf.get('sys', 'cfg_type')
        self['debug'] = cf.getboolean('sys', 'debug')
        for x in cf.items(config_type):
            self[x[0]] = x[1]
        return True

    def from_json(self, file_name):
        config_path = os.path.join(self.root_path, file_name)
        assert os.path.isfile(config_path), '缺少 %s 文件' % file_name
        with open(config_path) as f:
            data_str = f.read()
            data_json = ujson.loads(data_str)
        self.update(data_json)
        return True

    def get_version(self):
        g_git_HEAD = ''
        g_git_HEAD_hash = ''
        dotgit_path = os.path.join(self.root_path, '.git')
        if os.path.isdir(dotgit_path):
            git_HEAD_path = os.path.join(dotgit_path, 'HEAD')
            with open(git_HEAD_path, 'r') as f:
                g_git_HEAD = f.readline().strip()
            if g_git_HEAD.startswith('ref:'):
                git_hash_path = g_git_HEAD[5:]
                git_hash_path = os.path.join(dotgit_path, git_hash_path)
                g_git_HEAD = g_git_HEAD.split('/')[-1]
                with open(git_hash_path, 'r') as f:
                    g_git_HEAD_hash = f.readline().strip()
        git_version = ':'.join([g_git_HEAD, g_git_HEAD_hash])
        return git_version

config = Config()
config.from_ini('config.ini')
if config['debug']:
    config['git_version'] = config.get_version()
