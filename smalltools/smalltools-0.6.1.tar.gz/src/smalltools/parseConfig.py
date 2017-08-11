#!/usr/bin/env python
# -*- coding=utf-8 -*-
# Author: Jingyu Wang <badpasta@gmail.com>
# 
# Environment:
# Python by version 2.7.
# request = ['pyYaml']

from os.path import isdir
from yaml import load as yamlLoad
from re import match as re_match, search as re_search

import os
import sys


def _expYaml(d):

    fTmp = open(d)
    yTmp = yamlLoad(fTmp) # select for python dict
    fTmp.close()

    return yTmp


def parseParams(conf_Path):

    ''' trmap = ['record_api', 'config', 'domain_api', 'default'] '''

    found = filter(lambda x: isdir(x),
                    (conf_Path, '/etc/secdd/conf'))

    if not found:
        print "configuration directory is not exit!"
        sys.exit(0)

    recipe = found[0]
    trmap = dict()
    for root, dirs, files in os.walk(recipe):
        for filespath in files:
            if re_match('.*ml$', filespath):
                filename = re_search(r'(.*)\..*ml$', filespath).group(1)
                trmap[filename] = _expYaml(os.path.join(root, filespath))

    return trmap


def _checkParams(func):
    '''
        判断参数key是否存在.
    '''
    def the_func(self, *args, **kwargs):
        the_key = str()
        if len(args) and args[0] in self._options:
                the_key = args[0]

        if len(kwargs):
            for key in kwargs.keys():
                if key in self._options:
                    the_key = key
                    break

        if len(the_key):
            raise Error("Option %r already defined." 
                        %(the_key))

        return func(self, *args, **kwargs)

    return the_func


class ImitateOptions(object):
    def __init__(self):
        self._options = dict()

    def __getattr__(self, name):
        if self._options.has_key(name):
            return self._options[name]
        raise AttributeError("Unrecognized option %r" % name)

    def define(self, key, value):
        if key in self._options:
            raise Error("Option %r already defined." 
                        %(key))
        self._options[key] = value


class AdvancedOptions(object):
    '''
        通过递归方式解决文件夹中配置文件的名称与数值对应问题.
        PS: 配置文件中所有字典中的'key'都解析为实例.key.
        EXAMPLE::
            kw = {'aa': dict(bb='cc')}
            op = AdvancedOptions()
            op.define(**kw)

            print op.aa.bb 
    '''
    def __init__(self):
        self._options = dict()

    def __getattr__(self, name):
        if self._options.has_key(name):
            return self._options[name]
        raise AttributeError("Unrecognized option %r" % name)
    
    @_checkParams
    def define(self, **kw):
        for key, value in kw.items():
            self._options[key] = isinstance(value, dict) and \
                                 self._recursive(**value) or value

    @classmethod
    def _recursive(cls, **kw):
        _ops = cls()
        _ops.define(**kw)
        return _ops


class OtherOptions(AdvancedOptions):
    '''
        通过自定义options.key来确定一级参数政策.
        EXAMPLE:
        """ kw = {'aa': dict(bb='cc')}
            op = OtherOptions()
            op.addParam('aa')

            for key, value in kw['aa'].items():
                op.aa.define(key, value)

                print op.aa.bb 
        """
    '''
    @_checkParams
    def addParam(self, name):
        self._options[name] = OtherOptions()

    @_checkParams
    def define(self, key, value):
        self._options[key] = value


        

Options = ImitateOptions()
AdvOptions = AdvancedOptions()
OtherOpts = OtherOptions()
