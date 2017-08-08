from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse

# Create your tests here.
class CursoTestCase(TestCase):
	def setUp(self):
		self.client = Client()

	def test_clist(self):
		response = self.client.get(reverse('curso:search')+"?keyword=文化+臺灣&school=NUTC")
		self.assertEqual(type(response.json()), list)

	def test_incWeight(self):
		response = self.client.get(reverse('curso:incWeight')+'?keyword=發心&fullTitle=發展心理學')
		self.assertEqual(response.json(), {"receive Weight success": 1})