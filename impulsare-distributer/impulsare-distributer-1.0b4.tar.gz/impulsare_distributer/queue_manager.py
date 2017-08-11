import os

from impulsare_config import Reader as ConfigReader
from impulsare_logger import Logger
from redis import Redis
from rq import Queue as RedisQueue


class QueueManager():
    def __init__(self, config_file: str, listener: str):
        """Init the Queue from config parameters"""

        base_path = os.path.abspath(os.path.dirname(__file__))
        config_specs = base_path + '/static/specs.yml'
        config_default = base_path + '/static/default.yml'

        config = ConfigReader().parse(config_file, config_specs, config_default)
        config_listener = config.get('distributer')

        redis = Redis(config_listener['host'], config_listener['port'])

        if listener not in config:
            raise KeyError('You must have a key {} in your config with a sub-key queue'.format(listener))

        self._logger = Logger('distributer', config_file)
        self._logger.log.debug('Distributer QueueManager called')
        self._logger.log.debug('Connect to queue {}'.format(config[listener]['queue']))
        self._queue = RedisQueue(config[listener]['queue'], connection=redis)


    def add(self, method: str, item: str, job: str):
        """Put item into the queue."""

        return self._queue.enqueue(method, item, job=job)
