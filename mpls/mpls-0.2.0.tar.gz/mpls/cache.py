from .config import CACHE_DIR, CONFIG

import os
import shutil
import logging
import hashlib

logger = logging.getLogger(__name__)


class Cache(object):

    def __init__(self, cache_dir):
        self.cache_dir = cache_dir

    def __del__(self):
        if CONFIG['auto_clear_cache']:
            self.clear()

    def file_path(self, type, name):
        return os.path.join(self.host_folder(CONFIG['stylelib_url']), CONFIG['stylelib_format'].format(type=type, name=name))

    def host_folder(self, host_url):
        return os.path.join(self.cache_dir, hashlib.sha1(host_url.encode()).hexdigest())

    def is_cached(self, type, name):
        return os.path.exists(self.file_path(type, name))

    def add(self, type, name, content):
        if self.is_cached(type, name):
            return

        path = self.file_path(type, name)
        dir_path = os.path.dirname(path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        try:
            with open(path, 'w') as cache_file:
                cache_file.write(content)
        except OSError:
            pass

        logger.debug('added {} file "{}" to cache'.format(type, name))

    def clear(self, host_url=None):
        if not host_url:
            clean_up_dir = self.cache_dir
        else:
            clean_up_dir = self.host_folder(host_url)

        logger.debug('cleaning up cache for stylelib host: {}'.format(host_url))
        if os.path.exists(clean_up_dir):
            shutil.rmtree(clean_up_dir, ignore_errors=True)


CACHE = Cache(CACHE_DIR)


def clear_cache(host_url=None):
    """Clears the file cache of the specified host or the complete cache if host_url is
    not specified.

    Can be useful if the original style file has changed but an old version is still
    available in the cache. Alternatively you can call any of the frontend methods
    (get, use, temp) with the optional `ignore_cache` parameter.
    """
    CACHE.clear(host_url)
