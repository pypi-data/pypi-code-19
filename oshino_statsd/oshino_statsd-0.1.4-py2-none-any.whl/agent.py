import asyncio
import multiprocessing as mp

from oshino import Agent
from oshino_statsd import receiver


class Metric(object):

    def __init__(self, bucket, value, sampling=None):
        self.bucket = bucket
        self.value = value
        self.sampling = sampling

    @staticmethod
    def create(bucket, value, _type, sampling=None):
        if _type == "c":
            return Counter(bucket, value, sampling)
        elif _type == "ms":
            return Timer(bucket, value, sampling)
        elif _type == "g":
            return Gauge(bucket, value, sampling)
        elif _type == "s":
            return Set(bucket, value, sampling)
        else:
            raise RuntimeError("Unknown metric type: {0}".format(_type))

    def get_tags(self):
        name = self.__class__.__name__
        return [name.lower() + "s"]


class Counter(Metric):
    pass


class Timer(Metric):
    pass


class Gauge(Metric):
    pass


class Set(Metric):
    pass


def parse_metrics(msg):
    metrics = msg.decode("UTF-8").split("\n")
    for metric in metrics:
        if len(metric) == 0:
            continue
        head, tail = metric.split(":", 1)
        buff = tail.split("|")
        yield Metric.create(head, *buff)


class StatsdAgent(Agent):

    def __init__(self, cfg):
        super(StatsdAgent, self).__init__(cfg)
        self.queue = mp.Queue(maxsize=self.queue_size)

    def on_close(self):
        self.queue.close()
        self.queue.join_thread()

    def on_start(self):
        logger = self.get_logger()
        loop = asyncio.get_event_loop()
        self.proc = mp.Process(name="UDP server",
                               target=receiver.run,
                               args=(self.host, self.port, self.queue, logger))
        self.proc.daemon = True
        self.proc.start()

    @property
    def host(self):
        return self._data.get("host", "localhost")

    @property
    def port(self):
        return int(self._data.get("port", 8125))

    @property
    def queue_size(self):
        return int(self._data.get("queue-size", 1000))

    async def process(self, event_fn):
        loop = asyncio.get_event_loop()
        logger = self.get_logger()
        while not self.queue.empty():
            msg = self.queue.get()
            logger.debug("Got msg: {0}".format(msg))
            for m in parse_metrics(msg):
                logger.debug("Sending metric with name:{0} and value:{1}".format(self.prefix + m.bucket, m.value))
                event_fn(service=self.prefix + m.bucket,
                         metric_f=float(m.value),
                         tags=m.get_tags())
