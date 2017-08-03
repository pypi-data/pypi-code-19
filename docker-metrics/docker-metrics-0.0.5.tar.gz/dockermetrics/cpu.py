import os
import json
from .toolbox import *


class containerCPU(object):
    def __init__(self, containerId, sysfs='/sys/fs/cgroup',
                 cpuAcctPath='cpuacct/docker/',
                 cpuPath='cpu/docker/'):
        self.containerId = containerId
        self.cpuacct_path = os.path.join(sysfs, cpuAcctPath, str(containerId))
        self.cpu_path = os.path.join(sysfs, cpuPath, str(containerId))

        self.stats = {
            # total nanoseconds CPUs have been in use
            'usage': (0, 0),
            # Number of enforcement intervals that have elapsed
            'nr_periods': (0, 0),
            # Number of times the group has been throttled
            'nr_throttled': (0, 0),
            # Total time that members of the group were throttled,
            # in nanoseconds
            'throttled_time': (0, 0)
        }

        self.__collect()

    def __collect(self):
        self.stats['usage'] = get_data_single(
            os.path.join(self.cpuacct_path, 'cpuacct.usage'))

        self.stats.update(
            get_data_multi(
                os.path.join(self.cpu_path, 'cpu.stat'),
                ['nr_periods', 'nr_throttled', 'throttled_time']
            )
        )

    def dump(self):
        return json.dumps(self.stats)
