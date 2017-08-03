import os
import json
from .toolbox import *


class containerIO(object):
    def __init__(self, containerId, sysfs='/sys/fs/cgroup',
                 ioPath='blkio/docker/'):
        self.containerId = containerId
        self.path = os.path.join(sysfs, ioPath, str(containerId))

        self.stats = {
            # Number of bytes transferred to/from the disk
            'service_bytes_read': (0, 0),
            'service_bytes_write': (0, 0),
            'service_bytes_sync': (0, 0),
            'service_bytes_async': (0, 0),
            'service_bytes_total': (0, 0),
            # Number of IOs (bio) issued to the disk by the group
            'serviced_read': (0, 0),
            'serviced_write': (0, 0),
            'serviced_sync': (0, 0),
            'serviced_async': (0, 0),
            'serviced_total': (0, 0)
        }

        self.__collect()

    def __collect(self):
        service_bytes = get_data_selective(
            os.path.join(self.path, 'blkio.throttle.io_service_bytes'),
            items=['Read', 'Write', 'Sync', 'Async', 'Total']
        )
        self.stats['service_bytes_read'] = service_bytes['Read']
        self.stats['service_bytes_write'] = service_bytes['Write']
        self.stats['service_bytes_sync'] = service_bytes['Sync']
        self.stats['service_bytes_async'] = service_bytes['Async']
        self.stats['service_bytes_total'] = service_bytes['Total']

        serviced = get_data_selective(
            os.path.join(self.path, 'blkio.throttle.io_serviced'),
            items=['Read', 'Write', 'Sync', 'Async', 'Total']
        )

        self.stats['serviced_read'] = serviced['Read']
        self.stats['serviced_write'] = serviced['Write']
        self.stats['serviced_sync'] = serviced['Sync']
        self.stats['serviced_async'] = serviced['Async']
        self.stats['serviced_total'] = serviced['Total']

    def dump(self):
        return json.dumps(self.stats)
