import os

import psutil

from oshino import Agent


def iterate_fields(data):
    for field in data._fields:
        yield field, getattr(data, field)


def cpu_info():
    yield "cpu.total.perc", psutil.cpu_percent(interval=None)
    for i, cpu_perc in enumerate(psutil.cpu_percent(interval=None,
                                                    percpu=True)):
        yield "cpu.{0}.perc".format(i), cpu_perc

    for i, info in enumerate(psutil.cpu_times(percpu=True)):
        for k, v in iterate_fields(info):
            key = "cpu.{0}.times.{1}".format(i, k)
            yield key, v


def ram_info():
    mem = psutil.virtual_memory()

    for k, v in iterate_fields(mem):
        yield "ram.{0}".format(k), v


def swap_info():
    swap = psutil.swap_memory()
    for k, v in iterate_fields(swap):
        yield "swap.{0}".format(k), v


def disk_info(paths):
    # Disk usage
    for path in paths:
        for k, v in psutil.disk_usage(path):
            key = "disk.usage.{0}.{1}".format(path, k)
            yield key, v

    # Disk IO
    for k, v in iterate_fields(psutil.disk_io_counters()):
        key = "disk.io.{0}".format(k)
        yield key, v


def net_info():
    # Net IO
    net_info = psutil.net_io_counters()
    if isinstance(net_info, dict):
        for iface, info in net_info:
            for k, v in iterate_fields(info):
                key = "net.{0}.{1}".format(iface, k)
                yield key, v
    else:
        for k, v in iterate_fields(net_info):
            key = "net.{0}.{1}".format("eth0", k)
            yield key, v


def load_info():
    (shortterm, midterm, longterm) = os.getloadavg()
    yield "load.shortterm", shortterm
    yield "load.midterm", midterm
    yield "load.longterm", longterm


class HWAgent(Agent):

    @property
    def paths(self):
        """
        Paths in which you want to measure free space.
        Eg. '/' in unix to see free space on root
        """
        return self._data.get("paths", [])

    async def process(self, event_fn):
        logger = self.get_logger()
        data = []

        data.extend(cpu_info())
        data.extend(ram_info())
        data.extend(swap_info())
        data.extend(disk_info(self.paths))
        data.extend(net_info())
        data.extend(load_info())

        for name, metric in data:
            service_name = self.prefix + name
            logger.debug("Sending metric with name:{0} and value:{1}"
                         .format(service_name, metric))
            event_fn(service=service_name,
                     metric_f=float(metric))
