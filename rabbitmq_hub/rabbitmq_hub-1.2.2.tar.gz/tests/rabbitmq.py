#!/usr/bin/env python
# coding: utf-8
# Author: `mageia`,
# Email: ``,
# Date: `08/05/2017 15:17`
# Description: ''

import time
from unittest import TestCase
from ..rabbitmq_hub import PubSubHub, Pub, Sub


class RabbitMQTestCase(TestCase):
    @staticmethod
    def user_callback(topic, msg):
        print('user_callback: topic: %s, msg: %s' % (topic, msg))

    def get_hub(self):
        return PubSubHub(url='pubsub://leaniot:leaniot@119.254.211.60:5670/', queue_group='test')

    def test_hub_publish(self):
        p = self.get_hub()
        i = 1
        while True:
            msg = "message: %d" % i
            p.publish(msg, 'test.test.1')
            p.publish(msg, 'test.test.2')
            p.publish(msg, 'test.test.3')
            p.publish(msg, 'test.test.4')
            i += 1
            print('published %s messages' % (i))
            time.sleep(0.1)

    def test_hub_subscribe(self):
        h = self.get_hub()
        h.subscribe('test.test.1', self.user_callback)
        h.subscribe('test.test.2', self.user_callback)

        @h.subscribe('leaniot.realtime.data')
        @h.subscribe('test.test.3')
        @h.subscribe('test.test.4')
        def media_callback(topic, msg):
            print('media_callback: topic: %s, msg: %s' % (topic, msg))
        h.run()
        h.join()

    def test_pub(self):
        p = Pub()
        i = 1

        while True:
            msg = "message: %d" % i
            p.publish(msg, 'rabbitmq.dashboard.index')
            p.publish(msg, 'rabbitmq.device.registered')
            # p.publish(msg, 'rabbitmq.user.logout')
            #
            i += 1
            # msg = {'a': i}
            # p.publish(msg, 'rabbitmq.media.get')
            #
            # msg = ['aaaa', {'bb': time.time(), 'cc': '121231'}]
            # p.publish(msg, 'rabbitmq.media.upload')
            # print('published %s messages' % (i))
            time.sleep(0.1)

    def test_sub(self):
        s = Sub('test', '127.0.0.1', reconnect_interval=10)

        @s.subscribe('test.user.login')
        @s.subscribe('test.media.get')
        @s.subscribe('test.media.upload')
        def media_callback(topic, msg):
            print('media_callback: topic: %s, msg: %s' % (topic, msg))
        s.run()

