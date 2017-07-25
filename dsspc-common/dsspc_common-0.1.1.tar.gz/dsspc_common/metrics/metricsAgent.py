# -*- coding: utf-8 -*-
import time

from influxdb import InfluxDBClient
from ..metrics import Metrics

from ..utils.singleton import Singleton


class MetricsAgent(Singleton, Metrics):
    _sender = None

    def __init__(self, host, port=8086, username='root', password='root'):
        if not self._sender:
            self._sender = InfluxDBClient(
                host=host,
                port=port,
                username=username,
                password=password,
                database=None,
                ssl=False,
                verify_ssl=False,
                timeout=None,
                use_udp=False,
                udp_port=4444,
                proxies=None
            )

    def write_point(self, db, measurement, fields, tags, timestamp=None, batch_size=None):
        """
        write metrics to influxdb
        :param db: influxdb database name
        :type db: str
        :param measurement: from name
        :type measurement: str
        :param fields: select fields
        :type fields: dict
        :param tags: group by tags
        :type tags: dict
        :param timestamp: insert time
        :type timestamp: int 13
        :param batch_size: insert batch
        :type batch_size: int
        :return: True if successful else False
        """
        if timestamp is None:
            timestamp = int(time.time() * 1000)

        fields = {k: float(v) for k, v in fields.iteritems()}

        json_body = [
            {
                "measurement": measurement,
                "tags": tags,
                "time": timestamp,
                "fields": fields
            }
        ]
        return self._sender.write_points(json_body, database=db, time_precision='ms', batch_size=batch_size)

    def write_one_point(self, db, measurement, tags, value=1, timestamp=None, batch_size=None):
        fields = {
            'value': value
        }
        self.write_point(db, measurement, fields, tags, timestamp=timestamp, batch_size=batch_size)

    def query(self, db, query):
        return self._sender.query(query, database=db)
