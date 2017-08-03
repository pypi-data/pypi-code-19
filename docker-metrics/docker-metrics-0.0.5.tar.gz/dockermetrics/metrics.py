import json
import time
import logging

from dockermetrics import *

logger = logging.getLogger(__name__)

__version__ = '0.0.5'


class containerMetrics(object):
    def __init__(self, containerId, sysfs='/sys/fs/cgroup'):
        self.containerId = containerId
        self.sysfs = sysfs
        self.stats = {}

        self.__collect()

    def __collect(self):
        cpu = containerCPU(containerId=self.containerId, sysfs=self.sysfs)
        mem = containerMEM(containerId=self.containerId, sysfs=self.sysfs)
        io = containerIO(containerId=self.containerId, sysfs=self.sysfs)

        self.stats = {
            'cpu': cpu.stats,
            'mem': mem.stats,
            'io': io.stats,
            'clock': time.time()
        }

    def dump(self):
        return json.dumps(self.stats)
