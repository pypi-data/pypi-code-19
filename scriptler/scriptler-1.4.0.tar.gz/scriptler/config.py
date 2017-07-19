# -*- coding: utf-8 -*-
"""
.. module:: scriptler.config
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann a.friemann@automate.wtf

----------------------------------------------------------------------------
"THE BEER-WARE LICENSE" (Revision 42):
<aljosha.friemann@gmail.com> wrote this file.  As long as you retain this
notice you can do whatever you want with this stuff. If we meet some day,
and you think this stuff is worth it, you can buy me a beer in return.
----------------------------------------------------------------------------

"""

import logging, json, subprocess, os, copy, re

from scriptler.yaml import load, dump
from scriptler.model import Config, Script, Source

def parse_config(path, defaults):
    data = copy.deepcopy(defaults)
    data.update({'path': path})

    with open(path, 'r') as stream:
        try:
            data.update( load(stream) )
        except:
            pass

    return Config(**data)

def pretty_print(config):
    print(dump(config))

def edit(config):
    editor = os.environ.get('EDITOR')

    if editor is None:
        raise RuntimeError('Environment variable EDITOR is not set.')

    return subprocess.call([editor, config.path])

def save(config):
    with open(config.path, 'w') as stream:
        stream.write(dump(config))

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
