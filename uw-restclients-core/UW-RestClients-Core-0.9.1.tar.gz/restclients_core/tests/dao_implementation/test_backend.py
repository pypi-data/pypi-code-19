from unittest import TestCase, skipUnless
from restclients_core.dao import DAO, MockDAO
from restclients_core.cache import NoCache
from restclients_core.models import MockHTTP
from restclients_core.exceptions import ImproperlyConfigured


class TDAO(DAO):
    def service_name(self):
        return "backend_test"

    def get_default_service_setting(self, key):
        if "DAO_CLASS" == key:
            return ('restclients_core.tests.dao_implementation.'
                    'test_backend.Backend')


class TCDAO(TDAO):
    def get_cache(self):
        return Cache()


class E1DAO(TDAO):
    def get_default_service_setting(self, key):
        if "DAO_CLASS" == key:
            return ('restclients_core.tests.dao_implementation.'
                    'test_backendX.Backend')


class E2DAO(TDAO):
    def get_default_service_setting(self, key):
        if "DAO_CLASS" == key:
            return ('restclients_core.tests.dao_implementation.'
                    'test_backend.BackendX')


class TestBackend(TestCase):
    def test_get(self):
        response = TDAO().getURL('/ok')
        self.assertEquals(response.data, 'ok - GET')

    def test_post(self):
        response = TDAO().postURL('/ok')
        self.assertEquals(response.data, 'ok - POST')

    def test_put(self):
        response = TDAO().putURL('/ok', {}, '')
        self.assertEquals(response.data, 'ok - PUT')

    def test_delete(self):
        response = TDAO().deleteURL('/ok')
        self.assertEquals(response.data, 'ok - DELETE')

    def test_patch(self):
        response = TDAO().patchURL('/ok', {}, '')
        self.assertEquals(response.data, 'ok - PATCH')

    def test_error_level1(self):
        self.assertRaises(ImproperlyConfigured, E1DAO().getURL, '/ok')

    def test_error_level2(self):
        self.assertRaises(ImproperlyConfigured, E2DAO().getURL, '/ok')

    @skipUnless(hasattr(TestCase, 'assertLogs'), 'Python < 3.4')
    def test_log(self):
        with self.assertLogs('restclients_core.dao', level='INFO') as cm:
            response = TDAO().getURL('/ok')
            self.assertEquals(len(cm.output), 1)
            (msg, time) = cm.output[0].split(' time:')
            self.assertEquals(msg,
                              'INFO:restclients_core.dao:service:backend_test '
                              'method:GET url:/ok status:200 from_cache:no')
            self.assertGreater(float(time), 0)

        with self.assertLogs('restclients_core.dao', level='INFO') as cm:
            response = TDAO().putURL('/api', {}, '')
            self.assertEquals(len(cm.output), 1)
            (msg, time) = cm.output[0].split(' time:')
            self.assertEquals(msg,
                              'INFO:restclients_core.dao:service:backend_test '
                              'method:PUT url:/api status:200 from_cache:no')
            self.assertGreater(float(time), 0)

        # Cached response
        with self.assertLogs('restclients_core.dao', level='INFO') as cm:
            response = TCDAO().getURL('/ok')
            self.assertEquals(len(cm.output), 1)
            (msg, time) = cm.output[0].split(' time:')
            self.assertEquals(msg,
                              'INFO:restclients_core.dao:service:backend_test '
                              'method:GET url:/ok status:200 from_cache:yes')
            self.assertGreater(float(time), 0)

        # Cached post response
        with self.assertLogs('restclients_core.dao', level='INFO') as cm:
            response = TCDAO().getURL('/ok2')
            self.assertEquals(len(cm.output), 1)
            (msg, time) = cm.output[0].split(' time:')
            self.assertEquals(msg,
                              'INFO:restclients_core.dao:service:backend_test '
                              'method:GET url:/ok2 status:404 from_cache:yes')
            self.assertGreater(float(time), 0)


class Backend(MockDAO):
    def load(self, method, url, headers, body):
        response = MockHTTP()
        response.status = 200
        response.data = "ok - %s" % method
        return response


class Cache(NoCache):
    def getCache(self, service, url, headers):
        if url == '/ok':
            response = MockHTTP()
            response.status = 200
            response.data = 'ok - GET'
            return {'response': response}

    def processResponse(self, service, url, response):
        response.status = 404
        return {'response': response}
