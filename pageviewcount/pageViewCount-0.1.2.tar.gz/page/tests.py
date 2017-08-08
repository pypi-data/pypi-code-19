from django.test import TestCase
from django.test.client import Client

from page.models import ViewCount


class TestViewCount(TestCase):
    def setUp(self):
        ViewCount.objects.all().delete()
        print('view count test start....')

    def test_view_count(self):
        count = 10
        c = Client()
        for i in range(count):
            c.get('http://127.0.0.1:8000/app/')

        self.assertEqual(count, ViewCount.objects.filter(url='/app/').values('hits').count())

    def tearDown(self):
        print('test is finished')
