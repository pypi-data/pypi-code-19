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
            'service_bytes_read': 0,
            'service_bytes_write': 0,
            'service_bytes_sync': 0,
            'service_bytes_async': 0,
            'service_bytes_total': 0,
            # Number of IOs (bio) issued to the disk by the group
            'serviced_read': 0,
            'serviced_write': 0,
            'serviced_sync': 0,
            'serviced_async': 0,
            'serviced_total': 0,
        }

        self.__collect()

    def __collect(self):
        service_bytes = get_data_selective(
            os.path.join(self.path, 'blkio.throttle.io_service_bytes'))
        self.stats['service_bytes_read'] = service_bytes.get('Read', None)
        self.stats['service_bytes_write'] = service_bytes.get('Write', None)
        self.stats['service_bytes_sync'] = service_bytes.get('Sync', None)
        self.stats['service_bytes_async'] = service_bytes.get('Async', None)
        self.stats['service_bytes_total'] = service_bytes.get('Total', None)

        serviced = get_data_selective(
            os.path.join(self.path, 'blkio.throttle.io_serviced'))

        self.stats['serviced_read'] = serviced.get('Read', None)
        self.stats['serviced_write'] = serviced.get('Write', None)
        self.stats['serviced_sync'] = serviced.get('Sync', None)
        self.stats['serviced_async'] = serviced.get('Async', None)
        self.stats['serviced_total'] = serviced.get('Total', None)

    def dump(self):
        return json.dumps(self.stats)
