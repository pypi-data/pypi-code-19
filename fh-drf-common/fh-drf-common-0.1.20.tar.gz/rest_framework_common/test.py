import datetime
import errno
import inspect
import json
import os
import platform
import socket

from django.db import connections
from django.test.client import ClientHandler
from django.test.testcases import LiveServerTestCase, LiveServerThread
from google.appengine.api import apiproxy_stub_map, datastore_types
from google.appengine.ext import deferred, ndb, testbed
from rest_framework import status
from rest_framework.test import APITestCase, APITransactionTestCase

from freezegun import freeze_time as fg_freeze_time
from freezegun.api import FakeDatetime
from jsonschema import Draft4Validator
from mock import patch

_is_cpython = (
    hasattr(platform, 'python_implementation') and
    platform.python_implementation().lower() == "cpython"
)


# Need any async tasklets to run before request is complete since
# Django tests don't run through real wsgi handler we fake it here.
old_get_response = ClientHandler.get_response
@ndb.toplevel
def get_response(self, *args, **kwargs):
    return old_get_response(self, *args, **kwargs)
ClientHandler.get_response = get_response


class HTTPStatusTestCaseMixin(object):

    def assertHTTP200(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def assertHTTP201(self, response):
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def assertHTTP204(self, response):
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def assertHTTP400(self, response):
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def assertHTTP401(self, response):
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def assertHTTP403(self, response):
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def assertHTTP404(self, response):
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class _freeze_time(object):
    def __init__(self, *args, **kwargs):
        self._gae_patch = patch('google.appengine.ext.db.DateTimeProperty.data_type', new=FakeDatetime)
        self._freeze = fg_freeze_time(*args, **kwargs)
        datastore_types._VALIDATE_PROPERTY_VALUES[FakeDatetime] = datastore_types.ValidatePropertyNothing
        datastore_types._PACK_PROPERTY_VALUES[FakeDatetime] = datastore_types.PackDatetime
        datastore_types._PROPERTY_MEANINGS[FakeDatetime] = datastore_types.entity_pb.Property.GD_WHEN

    def __call__(self, func):
        if inspect.isclass(func):
            return self._freeze.decorate_class(func)
        return self._freeze.decorate_callable(func)

    def start(self):
        self._freeze.start()
        self._gae_patch.start()

    def stop(self):
        self._freeze.stop()
        self._gae_patch.stop()

    def __enter__(self):
        return self.start()

    def __exit__(self, *args):
        self.stop()


def freeze_time(time_to_freeze=None, tz_offset=0, ignore=None, tick=False):
    # Python3 doesn't have basestring, but it does have str.
    try:
        string_type = basestring
    except NameError:
        string_type = str

    if not isinstance(time_to_freeze, (string_type, datetime.date)):
        raise TypeError(('freeze_time() expected None, a string, date instance, or '
                         'datetime instance, but got type {0}.').format(type(time_to_freeze)))
    if tick and not _is_cpython:
        raise SystemError('Calling freeze_time with tick=True is only compatible with CPython')

    if ignore is None:
        ignore = []
    ignore.append('six.moves')
    ignore.append('django.utils.six.moves')
    return _freeze_time(time_to_freeze, tz_offset, ignore, tick)


class ClientHelperMixin(object):

    def validate(self, data, schema):
        v = Draft4Validator(schema)
        if not v.is_valid(data):
            for error in sorted(v.iter_errors(data), key=str):
                if error.context:
                    self.fail("\n".join('{} {}'.format(cerror.absolute_path, cerror.message) for cerror in error.context))
                else:
                    self.fail(error.message)

    def validate_retrieve(self, response, schema):
        self.validate(response.data, schema)

    def validate_list(self, response, schema, pages=True):
        if pages:
            self.validate(response.data['results'][0], schema['items']['oneOf'][0])
            self.validate(response.data['results'], schema)
        else:
            self.validate(response.data[0], schema['items']['oneOf'][0])
            self.validate(response.data, schema)

    def get(self, path, data=None, follow=False, secure=False, **extra):
        print '***' * 15
        print 'GET {}'.format(path)
        print 'Authenticated' if '_auth_user_id' in self.client.session else 'Not Authenticated'
        response = self.client.get(path=path, data=data, follow=follow, secure=secure, **extra)
        print 'Response status code: {}'.format(response.status_code)
        if hasattr(response, 'data'):
            print 'Response body:'
            print json.dumps(response.data)
        return response

    def post(self, path, data=None, content_type=None, follow=False, secure=False, **extra):
        print '***' * 15
        print 'POST {}'.format(path)
        print 'Authenticated' if '_auth_user_id' in self.client.session else 'Not Authenticated'
        print 'Request body:'
        print json.dumps(data)
        response = self.client.post(path=path, data=data, content_type=content_type, follow=follow, secure=secure,
                                    **extra)
        print 'Response status code: {}'.format(response.status_code)
        print 'Response body:'
        if response.status_code != 204:
            print json.dumps(response.data)
        return response

    def patch(self, path, data=None, content_type=None, follow=False, secure=False, **extra):
        print '***' * 15
        print 'PATCH {}'.format(path)
        print 'Authenticated' if '_auth_user_id' in self.client.session else 'Not Authenticated'
        print 'Request body:'
        print json.dumps(data)
        response = self.client.patch(path=path, data=data, content_type=content_type, follow=follow, secure=secure,
                                     **extra)
        print 'Response status code: {}'.format(response.status_code)
        print 'Response body:'
        print json.dumps(response.data)
        return response

    def put(self, path, data=None, content_type=None, follow=False, secure=False, **extra):
        print '***' * 15
        print 'PUT {}'.format(path)
        print 'Authenticated' if '_auth_user_id' in self.client.session else 'Not Authenticated'
        print 'Request body:'
        print json.dumps(data)
        response = self.client.put(path=path, data=data, content_type=content_type, follow=follow, secure=secure,
                                   **extra)
        print 'Response status code: {}'.format(response.status_code)
        print 'Response body:'
        print json.dumps(response.data)
        return response

    def delete(self, path, data=None, content_type=None, follow=False, secure=False, **extra):
        print '***' * 15
        print 'DELETE {}'.format(path)
        print 'Authenticated' if '_auth_user_id' in self.client.session else 'Not Authenticated'
        print 'Request body:'
        print json.dumps(data)
        response = self.client.delete(path=path, data=data, content_type=content_type, follow=follow, secure=secure,
                                      **extra)
        print 'Response status code: {}'.format(response.status_code)
        print 'Response body:'
        print json.dumps(response.data)
        return response


class GAEHelperMixin(object):

    def setUp(self):

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../'))
        self.testbed.init_taskqueue_stub(root_path=path)
        self.testbed.init_memcache_stub()
        self.testbed.init_datastore_v3_stub()
        self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

        self.apiproxy = self.testbed._test_stub_map

        super(GAEHelperMixin, self).setUp()

    @ndb.toplevel
    def sync_tasks(self):
        """
        Because we use ndb.tasklet to submit to tasks to queues there can be one's that haven't submitted yet
        call this method to make sure they get submitted before moving on. We already wrap this in common places
        like using self.post, self.get so you won't need to use it there.
        :return:
        """
        pass

    def delete_task(self, task):
        self.taskqueue_stub.DeleteTask(task.headers['X-AppEngine-QueueName'], task.name)

    def delete_tasks(self, tasks):
        for task in tasks:
            self.delete_task(task)

    def flush_queues(self):
        self.sync_tasks()
        queues = self.taskqueue_stub.GetQueues()
        for queue in queues:
            self.taskqueue_stub.FlushQueue(queue['name'])

    @ndb.toplevel
    def run_taskqueue(self, url):
        tasks = self.taskqueue_stub.get_filtered_tasks(url)
        for task in tasks:
            deferred.run(task.payload)
            self.delete_task(task)

    def run_taskqueues(self, urls):
        for url in urls:
            self.run_taskqueue(url)


class TestCase(HTTPStatusTestCaseMixin, ClientHelperMixin, GAEHelperMixin, APITestCase):
    pass


class TransactionTestCase(HTTPStatusTestCaseMixin, ClientHelperMixin, GAEHelperMixin, APITransactionTestCase):
    pass


class LiveServerThread(LiveServerThread):
    """
    Thread for running a live http server while the tests are running.
    """
    def __init__(self, host, possible_ports, static_handler, connections_override=None):
        from google.appengine.api import apiproxy_stub_map
        self.apiproxy = apiproxy_stub_map.apiproxy

        super(LiveServerThread, self).__init__(host, possible_ports, static_handler, connections_override)

    def run(self):
        """
        Sets up the live server and databases, and then loops over handling
        http requests.
        """
        if self.connections_override:
            # Override this thread's database connections with the ones
            # provided by the main thread.
            for alias, conn in self.connections_override.items():
                connections[alias] = conn

        apiproxy_stub_map.apiproxy = self.apiproxy

        try:
            # This ensures that all ndb tasklets are ran before request is finished
            from django.core.wsgi import get_wsgi_application
            from google.appengine.ext import ndb
            from djangae.wsgi import DjangaeApplication
            handler = ndb.toplevel(DjangaeApplication(get_wsgi_application()))

            # Go through the list of possible ports, hoping that we can find
            # one that is free to use for the WSGI server.
            for index, port in enumerate(self.possible_ports):
                try:
                    self.httpd = self._create_server(port)
                except socket.error as e:
                    if (index + 1 < len(self.possible_ports) and
                                e.errno == errno.EADDRINUSE):
                        # This port is already in use, so we go on and try with
                        # the next one in the list.
                        continue
                    else:
                        # Either none of the given ports are free or the error
                        # is something else than "Address already in use". So
                        # we let that error bubble up to the main thread.
                        raise
                else:
                    # A free port was found.
                    self.port = port
                    break

            self.httpd.set_app(handler)
            self.is_ready.set()
            self.httpd.serve_forever()
        except Exception as e:
            self.error = e
            self.is_ready.set()


class LiveServerTestCase(HTTPStatusTestCaseMixin, ClientHelperMixin, LiveServerTestCase):

    @classmethod
    def setUpClass(cls):

        cls.testbed = testbed.Testbed()
        cls.testbed.activate()
        path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../'))
        cls.testbed.init_taskqueue_stub(root_path=path)
        cls.testbed.init_memcache_stub()
        cls.testbed.init_datastore_v3_stub()
        cls.taskqueue_stub = cls.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

        # Make the apiproxy available for other uses
        cls.apiproxy = cls.testbed._test_stub_map

        super(LiveServerTestCase, cls).setUpClass()

    @classmethod
    def _create_server_thread(cls, host, possible_ports, connections_override):
        return LiveServerThread(
            host,
            possible_ports,
            cls.static_handler,
            connections_override=connections_override
        )

    @ndb.toplevel
    def sync_tasks(self):
        """
        Because we use ndb.tasklet to submit to tasks to queues there can be one's that haven't submitted yet
        call this method to make sure they get submitted before moving on. We already wrap this in common places
        like using self.post, self.get so you won't need to use it there.
        :return:
        """
        pass

    def delete_task(self, task):
        self.taskqueue_stub.DeleteTask(task.headers['X-AppEngine-QueueName'], task.name)

    def delete_tasks(self, tasks):
        for task in tasks:
            self.delete_task(task)

    def flush_queues(self):
        self.sync_tasks()
        queues = self.taskqueue_stub.GetQueues()
        for queue in queues:
            self.taskqueue_stub.FlushQueue(queue['name'])

    @ndb.toplevel
    def run_taskqueue(self, url):
        tasks = self.taskqueue_stub.get_filtered_tasks(url)
        for task in tasks:
            deferred.run(task.payload)
            self.delete_task(task)

    def run_taskqueues(self, urls):
        for url in urls:
            self.run_taskqueue(url)
