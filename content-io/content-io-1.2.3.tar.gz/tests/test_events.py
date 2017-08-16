# coding=utf-8
import cio
from cio import events
from cio.utils.uri import URI
from cio.utils.imports import import_class
from tests import BaseTest


# class EventsTest(BaseTest):

    # def callback(self, a, b, **kwargs):
        # self.assertEqual(a, 'a')
        # self.assertEqual(b, 'b')
        # self.assertSetEqual(set(kwargs.keys()), {'c', 'd'})
        # self.assertEqual(kwargs['c'], 'c')
        # kwargs['d']['called'] = True  # callback answer

    # def test_listen(self):
        # d = dict(called=False)
        # events.listen('foo', self.callback)
        # events.trigger('foo', 'a', 'b', c='c', d=d)
        # self.assertTrue(d['called'])

    # def test_mute(self):
        # d = dict(called=False)
        # events.listen('foo', self.callback)
        # events.mute('foo', self.callback)
        # events.trigger('foo', 'a', 'b', c='c', d=d)
        # self.assertFalse(d['called'])

    # def test_publish(self):
        # node = cio.set('sv-se@label/email', u'e-post', publish=False)
        # self.assertEqual(node.uri, 'i18n://sv-se@label/email.txt#draft')
        # self.assertKeys(node.meta, 'modified_at', 'is_published')

        # node = cio.publish(node.uri)
