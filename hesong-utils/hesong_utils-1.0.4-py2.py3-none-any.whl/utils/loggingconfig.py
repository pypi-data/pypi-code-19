# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging.config
import os.path
from io import FileIO

try:
    import yaml
except ImportError:
    yaml = None
else:
    try:
        from yaml import CLoader as YamlLoader
    except ImportError:
        from yaml import Loader as YamlLoader

from .jsonutils import json_loads

__all__ = ['logging_config']


def logging_config(fname):
    _, ext = os.path.splitext(fname)
    if ext == '.yaml':
        if yaml:
            config = yaml.load(FileIO(fname), YamlLoader)
            logging.config.dictConfig(config)
        else:
            raise RuntimeError('yaml package not installed')
    elif ext == '.json':
        config = json_loads(open(fname).read())
        logging.config.dictConfig(config)
    elif ext == '.ini':
        logging.config.fileConfig(fname)
    else:
        raise RuntimeError('Unknown logging config file ext name: {}'.format(fname))
