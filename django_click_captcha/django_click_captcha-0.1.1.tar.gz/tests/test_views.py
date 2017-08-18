from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import SimpleTestCase, override_settings


# Create your tests here.
@override_settings(ROOT_URLCONF='tests.demo.urls')
class CaptchaViewTest(SimpleTestCase):
    allow_database_queries = False

    def test_get_captcha(self):
        response = self.client.get(reverse('click_captcha', kwargs=dict(uuid='abc')))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._headers.get('content-type'), ('Content-Type', 'image/png'))
        self.assertTrue(cache.get('abc'))

    def test_get_captcha_without_uuid(self):
        """超过 cache key 的长度"""
        a = 1000 * 'a'
        response = self.client.get('/vendor/click_captcha/{}/'.format(a))
        self.assertEqual(response.status_code, 404)
