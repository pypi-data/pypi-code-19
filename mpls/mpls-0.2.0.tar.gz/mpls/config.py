import os
import json
import logging

logger = logging.getLogger(__name__)

MPLS_TYPES = ('context', 'style', 'palette')

CONFIG_DIR = os.path.expanduser('~/.mpls')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
CONFIG = {
    'stylelib_url': "https://raw.githubusercontent.com/scruffy-t/mpls/master/stylelib/",
    'stylelib_format': "{type}/{name}.json",
    'auto_clear_cache': False,
    'enable_logging': False
}

CACHE_DIR = os.path.join(CONFIG_DIR, 'cache')


def load_config():
    global CONFIG
    try:
        CONFIG = json.load(open(CONFIG_FILE, 'r'))
        logger.debug('using config file {}'.format(CONFIG_FILE))
    except OSError:
        logger.debug('no config file found, using default config')

    if CONFIG['enable_logging']:
        logging.basicConfig(level=logging.DEBUG)

load_config()


def configure(save=False, **kwargs):
    """

    Parameters
    ----------
    save: bool
        save config to file after it was updated
    kwargs:
    - stylelib_url: str

    - stylelib_format: str

    - auto_clear_cache: bool

    - enable_logging: bool

    """
    if 'stylelib_url' in kwargs:
        # TODO: is it safe to do that with a web URL?
        kwargs['stylelib_url'] = os.path.expanduser(kwargs['stylelib_url'])

    CONFIG.update(kwargs)

    if save:
        if not os.path.exists(CONFIG_DIR):
            os.mkdir(CONFIG_DIR)
        json.dump(CONFIG, open(CONFIG_FILE, 'w'))
        logger.debug('saved customized config to {}'.format(CONFIG_FILE))
