from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse

# Create your tests here.
class CursoTestCase(TestCase):
	def setUp(self):
		self.client = Client()

	def test_CourseOfTime(self):
		response = self.client.get(reverse('cphelper:CourseOfTime')+"?day=1&time=5&school=NUTC&dept=通識類+多媒")
		self.assertEqual(type(response.json()), list)

	def test_CourseOfDept(self):
		response = self.client.get(reverse('cphelper:CourseOfDept')+'?dept=美容&school=NUTC&grade=三Ｂ')
		self.assertEqual(type(response.json()), dict)

	def test_Genra(self):
		response = self.client.get(reverse('cphelper:Genra')+'?school=NUTC')
		self.assertEqual(type(response.json()), dict)