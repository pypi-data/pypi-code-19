# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase,override_settings
from urltrace.models import UrlTrace,UrlTraceGroup
from urltrace import constants
from django.test import Client
from urltrace.middleware import  UrlTraceMiddleware

@override_settings(ROOT_URLCONF='urltrace.tests.urls')
@override_settings(DEBUG=True)
class ActionsTestCase(TestCase):
    def setUp(self):
        # create a group name
        url_trace_group = UrlTraceGroup(
            group_name="group_name_test",
            description="group name test"
        )
        url_trace_group.save()
        url_trace = UrlTrace(
            url_trace="/url_trace/1",
            url_trace_group=url_trace_group,
            description="url trace test 1 group name group_name_test"
        )
        url_trace.save()
        # registro del group trace general
        url_trace_group = UrlTraceGroup.objects.get(id=constants.DEFAULT_REGISTER)
        url_trace = UrlTrace(
            url_trace="/url_trace/2",
            url_trace_group=url_trace_group,
            description="url trace test 2 group name general"
        )
        url_trace.save()

        self.middleware = UrlTraceMiddleware()
        self.client = Client()
        self.request = self.client.get('/url_trace3/')

        pass

    def test_register_url_trace(self):
        url_trace = UrlTrace.objects.get(url_trace="/url_trace/1")
        print url_trace.description + " - " + url_trace.url_trace_group.group_name

        url_trace = UrlTrace.objects.get(url_trace="/url_trace/2")
        print url_trace.description + " - " + url_trace.url_trace_group.group_name

        pass

    def test_url_trace_middleware(self):
        self.request._closable_objects[0].META["HTTP_REFERER"] = "m.facebook.com/"
        self.request._closable_objects[0].META["HTTP_HOST"] = "www.crehana.com/"

        self.middleware.process_request(self.request._closable_objects[0])
        url_trace = UrlTrace.objects.filter(url_trace="m.facebook.com/")
        if len(url_trace)>0:
            print "Url create : " + url_trace[0].url_trace + ":" + url_trace[0].url_trace_group.group_name

        pass