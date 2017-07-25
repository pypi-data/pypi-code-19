from .config import CACHE_DIR, CONFIG

import os
import shutil
import logging

logger = logging.getLogger(__name__)


class Cache(object):

    def __init__(self, cache_dir):
        self.cache_dir = cache_dir

    def __del__(self):
        self.clear()

    def file_path(self, stype, name):
        return os.path.join(self.cache_dir, CONFIG['stylelib_url'].format(type=stype, name=name))

    def is_cached(self, stype, name):
        return os.path.exists(self.file_path(stype, name))

    def add(self, stype, name, content):
        if not CONFIG['enable_cache']:
            return
        if self.is_cached(stype, name):
            return

        path = self.file_path(stype, name)
        dir_path = os.path.dirname(path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        try:
            with open(path, 'w') as cache_file:
                cache_file.write(content)
        except OSError:
            pass

        logger.debug('added {} file "{}" to cache'.format(stype, name))

    def clear(self):
        logger.debug('cleaning up cache dir: {}'.format(self.cache_dir))
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir, ignore_errors=True)


CACHE = Cache(CACHE_DIR)


def clear_cache():
    """Clears the complete file cache.

    Can be useful if the underlying style file has changed but an old version is still
    available in the cache. Alternatively you can call any of the frontend methods
    (get, use, temp) with the optional `ignore_cache` parameter.
    """
    CACHE.clear()
