import os
import json
from collections import OrderedDict


class CacheService(object):

    __cache_path = str()
    __cache_root = str()

    def __init__(self, cache_root="", cache_path=""):
        self.__cache_root = cache_root
        self.__cache_path = cache_path

    def get_cached_data(self, cache_name, cache_file_id):
        cache_file = "{0}/{1}/json/{2}/{3}.json".format(self.__cache_root, self.__cache_path, cache_name, cache_file_id)

        if os.path.isfile(cache_file):
            return self.read_file(cache_file)
        else:
            return False

    def write_cache_data(self, cache_name, cache_file_id, data):
        cache_file = "{0}/{1}/json/{2}/{3}.json".format(self.__cache_root, self.__cache_path, cache_name, cache_file_id)
        return self.write_file(cache_file, data)

    def remove_cached_data(self, cache_name, cache_file_id):
        cache_file = "{0}/{1}/json/{2}/{3}.json".format(self.__cache_root, self.__cache_path, cache_name, cache_file_id)
        return self.remove_file(cache_file)

    @staticmethod
    def read_file(file_name):
        handle = open(file_name, "r")
        json_data = json.loads(handle.read(), object_pairs_hook=OrderedDict)
        handle.close()
        return json_data

    @staticmethod
    def write_file(file_name, data):
        handle = open(file_name, "w+")
        handle.write(json.dumps(data))
        handle.close()
        return True

    @staticmethod
    def remove_file(file_name):
        if os.path.isfile(file_name):
            os.unlink(file_name)
            return True
        else:
            return False
