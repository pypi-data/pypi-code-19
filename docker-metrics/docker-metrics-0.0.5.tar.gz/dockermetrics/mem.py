import os
import json
from .toolbox import *


class containerMEM(object):
    def __init__(self, containerId, sysfs='/sys/fs/cgroup',
                 memPath='memory/docker/'):
        self.containerId = containerId
        self.path = os.path.join(sysfs, memPath, str(containerId))

        self.stats = {
            # Total memory used in bytes: cached + rss
            'usage': 0,
            # Total memory used + swap in use in bytes
            'memsw_usage': 0,
            # Number of times memory usage hit limits
            'failcnt': 0,
            # Memory limit of the cgroup in bytes
            'limit': 0
        }

        self.__collect()

    def __collect(self):
        self.stats['usage'] = get_data_single(
            os.path.join(self.path, 'memory.usage_in_bytes'))
        self.stats['memsw_usage'] = get_data_single(
            os.path.join(self.path, 'memory.memsw.usage_in_bytes'))
        self.stats['failcnt'] = get_data_single(
            os.path.join(self.path, 'memory.failcnt'))
        self.stats['limit'] = get_data_single(
            os.path.join(self.path, 'memory.limit_in_bytes'))
        # If number is too high, limit is not set at all
        if (self.stats['limit'][1] == 0 and
           self.stats['limit'][0] > 1099511627776):
            self.stats['limit'] = (0, 0)

    def dump(self):
        return json.dumps(self.stats)
