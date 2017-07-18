# -*- coding: utf-8 -*-
import json
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

__all__ = ['logging_config']


def logging_config(fname):
    _, ext = os.path.splitext(fname)
    if ext == '.yaml':
        if yaml:
            config = yaml.load(FileIO(fname), YamlLoader)
            logging.config.dictConfig(config)
        else:
            raise RuntimeError('YAML not supported')
    elif ext == '.json':
        config = json.loads(open(fname).read())
        logging.config.dictConfig(config)
    elif ext == '.ini':
        logging.config.fileConfig(fname)
    else:
        raise RuntimeError('Unknown logging config file ext name: {}'.format(fname))
