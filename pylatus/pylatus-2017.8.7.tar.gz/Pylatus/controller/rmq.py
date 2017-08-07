#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import socket
import kombu
import auxygen
from PyQt5 import QtCore
from pylatus_brokers import constants as bc, tools
from .config import Config
from ..gui.gutils import GUtils


class RabbitMQ(QtCore.QObject):
    sigConnected = QtCore.pyqtSignal()
    sigDisconnected = QtCore.pyqtSignal()
    sigScanValue = QtCore.pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        self.address = None
        self.host = None
        self.port = None
        self.connection = None
        self.producer = None
        self.running = False
        self.reconnecting = False
        self.timer = None
        self.logger = auxygen.devices.logger.Logger('RabbitMQ')

    def setConfig(self):
        if Config.RabbitMQAddress == self.address:
            return
        self.address = Config.RabbitMQAddress
        self.host, self.port = tools.get_hostport(self.address)
        if self.running:
            self.start()

    def start(self):
        self.running = True
        self.timer = QtCore.QTimer()
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.drainEvents)
        self.connect()

    def connect(self):
        self._disconnect()
        if not self.host or not self.port:
            return False
        self.connection = kombu.Connection(f'amqp://{self.host}:{self.port}//')
        try:
            self.connection.connect()
        except socket.error as err:
            self._disconnect()
            self.logger.error(f'Could not connect to {self.host}:{self.port}: {str(err)}')
            return False
        channel = self.connection.channel()
        exchange = kombu.Exchange(bc.EXCHANGE_DCU, type='fanout', durable=False)
        self.producer = kombu.Producer(exchange=exchange, channel=channel, routing_key='', serializer='pickle')
        exchange_scan = kombu.Exchange(bc.EXCHANGE_SCAN, type='fanout', durable=False)
        queue = kombu.Queue(bc.EXCHANGE_SCAN, exchange_scan, channel=channel)
        self.consumer = kombu.Consumer(channel, queue, no_ack=True, prefetch_count=1, on_message=self.processScan)
        self.consumer.consume()
        self.sigConnected.emit()
        self.logger.info(f'Connected to {self.host}:{self.port}. Declared the exchange {bc.EXCHANGE_DCU}')
        return True

    def stop(self):
        self.running = False
        self._disconnect()

    def _disconnect(self):
        if self.connection:
            self.connection.release()
            self.logger.warn(f'Disconnected from {self.host}:{self.port}')
        self.connection = None
        self.producer = None
        self.consumer = None
        self.sigDisconnected.emit()

    def send(self, obj):
        if not self.connection:
            return
        if self.connection.connected:
            try:
                self.producer.publish(obj)
            except OSError as err:
                self.logger.warn(f'RabbitMQ has gone: {str(err)}. Trying to reconnect...')
                self.reconnect()
                QtCore.QTimer.singleShot(int(self.reconnecting) * 1000, lambda: self.send(obj))

    def reconnect(self):
        if not self.reconnecting:
            self.reconnecting = True
            while self.running:
                self.logger.warning('Trying to reconnect to RabbitMQ in 1 second')
                GUtils.delay(1000)
                if self.connect():
                    break
            self.reconnecting = False

    def sendChunk(self, opts):
        self.send(opts)

    def processScan(self, message):
        name, value = json.loads(message.payload)
        self.sigScanValue.emit(name, value)

    def drainEvents(self):
        if self.running and self.connection and self.connection.connected and not self.reconnecting:
            try:
                self.connection.drain_events(timeout=0.01)
            except socket.timeout:
                pass

    def scanStarted(self):
        self.timer.start(10)

    def scanFinished(self):
        self.timer.stop()
