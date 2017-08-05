from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse

# Create your tests here.
class CursoTestCase(TestCase):
	def setUp(self):
		self.client = Client()

	def test_CourseOfTime(self):
		response = self.client.get(reverse('cphelper:CourseOfTime')+"?day=1&time=5&school=NUTC&dept=通識類+多媒")
		self.assertEqual(response.json(), ["D19078", "D19013", "D19011", "D19080", "D19012", "D19009", "D19082", "D16162", "D16173", "D16142"])

	def test_CourseOfDept(self):
		response = self.client.get(reverse('cphelper:CourseOfDept')+'?dept=美容&school=NUTC&grade=三Ｂ')
		self.assertEqual(response.json(), {"optional": {"\u4e09\uff22": ["D19777"]}, "obligatory": {"\u4e09\uff22": ["D17772", "D17767", "D17768", "D17770", "D17766", "D17769", "D17771"]}})

	def test_Genra(self):
		response = self.client.get(reverse('cphelper:Genra')+'?school=NUTC')
		self.assertEqual(type(response.json()), type({}))