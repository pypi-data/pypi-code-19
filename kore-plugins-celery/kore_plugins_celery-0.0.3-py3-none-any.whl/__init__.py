from collections import defaultdict

from celery import Celery
from celery import signals

from kore import config_factory, container_factory
from kore.configs.exceptions import ConfigPluginNotFoundError
from kore_shell.lib.parsers import KVParser

__author__ = 'Artur Maciąg'
__email__ = 'maciag.artur@gmail.com'
__version__ = '0.0.3'
__url__ = 'https://github.com/kore-plugins/kore-plugins-celery'


def add_preload_options(parser):
    parser.add_argument('--config-type', default='dict')
    parser.add_argument('--config-opt', type=KVParser().parse,
                        action='append', default=[])


def merge_dict(*dicts):
    d = defaultdict(dict)
    for dd in dicts:
        for k, v in dd.items():
            d[k] = v
    return d


def on_preload_parsed(sender, signal, app, options, **kwargs):
    try:
        config_type = options['config_type']
        config_opt = merge_dict(*options['config_opt'])
        config = config_factory.create(config_type, **config_opt)
    except ConfigPluginNotFoundError as e:
        sender.die('ConfigPluginNotFoundError!', e)

    initial = {
        'config': config,
        'kore.components.celery.application': application,
    }
    container_factory.create(**initial)

application = Celery()
application.user_options['preload'].add(add_preload_options)

signals.user_preload_options.connect(on_preload_parsed)
