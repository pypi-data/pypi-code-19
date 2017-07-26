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
        return PubSubHub(url='pubsub://leaniot:leaniot@127.0.0.1:5672/', queue_group='test')

    def test_hub_publish(self):
        p = self.get_hub()
        i = 1
        while True:
            msg = "message: %d" % i
            p.publish(msg, 'rabbitmq.test.1')
            p.publish(msg, 'rabbitmq.test.2')
            p.publish(msg, 'rabbitmq.test.3')
            p.publish(msg, 'rabbitmq.test.4')
            i += 1
            print('published %s messages' % (i))
            time.sleep(0.1)

    def test_hub_subscribe(self):
        h = self.get_hub()
        h.subscribe('rabbitmq.test.1', self.user_callback)
        h.subscribe('rabbitmq.test.2', self.user_callback)

        @h.subscribe('rabbitmq.test.3')
        @h.subscribe('rabbitmq.test.4')
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
        s.subscribe('rabbitmq.user.login', self.user_callback)
        s.subscribe('rabbitmq.user.logout', self.user_callback)

        @s.subscribe('rabbitmq.user.login')
        @s.subscribe('rabbitmq.media.get')
        @s.subscribe('rabbitmq.media.upload')
        def media_callback(topic, msg):
            print('media_callback: topic: %s, msg: %s' % (topic, msg))
        s.run()

