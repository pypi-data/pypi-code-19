import logging

from datetime import datetime
from collections import defaultdict

class Stats(object):

    def __init__(self, logger=logging.getLogger()):
        """Creates a new stats object"""
        self.calls = defaultdict(int)
        self.start_time = datetime.now()
        self.last_touched = datetime.now()
        self.logger = logger

    def incr(self, call):
        """Increments a call and indicates that there was data sent recently"""
        self.calls[call] += 1
        self.last_touched = datetime.now()

    def log(self):
        """Logs out the current stats"""
        log = self.logger
        now = datetime.now()
        time_diff = now-self.start_time

        for call in self.calls:
            count = self.calls[call]
            log.info("source_client: %s calls: %s, (%s/s)", call, count, float(count) / time_diff.total_seconds())
