# -*- coding: utf-8 -*-
from django.apps import AppConfig
import urllib, requests, json
from timetable.models import Course

class SearchConfig(AppConfig):
    name = 'curso'
    
class SearchOb(object):
	"""docstring for SearchOb"""
	def __init__(self, keyword="", school=None, uri=None):
		from pymongo import MongoClient
		self.client = MongoClient(uri)
		self.db = self.client['timetable']
		self.SrchCollect = self.db['CourseSearch']
		self.TitleAbbre = self.db['TitleAbbre']

		self.keyword = keyword.split()
		self.school = school
		self.result = tuple()

	def getResult(self):
		self.doSearch()
		return self.result

	def doSearch(self):
		if len(self.keyword) == 1:
			self.keyword = self.keyword[0]
			self.result = self.KEMSearch(self.keyword)
		else:
			self.result = self.TCsearch()

	def KEMSearch(self, kw):
		from functools import reduce 

		cursor = self.SrchCollect.find({'key':kw}, {'value':1, '_id':False}).limit(1)
		if cursor.count() > 0:
			# Key Exist
			return list(cursor)[0]['value']
		else:
			try:
				kcm = json.loads(requests.get('http://140.120.13.244:10000/kcm/?keyword={}&lang=cht&num=200'.format(urllib.parse.quote(kw))).text)
				kem = json.loads(requests.get('http://140.120.13.244:10000/kem/?keyword={}&lang=cht&num=200'.format(urllib.parse.quote(kw))).text)


				for i in reduce(lambda x, y: x + y, zip(kcm, kem)):
					cursor = self.SrchCollect.find({'key':i[0]}, {self.school:1, '_id':False}).limit(1)
					if cursor.count() > 0:
						# Key Exist
						value = list(cursor)[0][self.school]
						self.SrchCollect.update({'key':kw}, {'$set': {self.school:value}}, upsert=True)
						return value

				return []
			except Exception as e:
				print(e)
				return []

	def TCsearch(self):
		cursor1 = self.KEMSearch(self.keyword[0])
		cursor2 = self.KEMSearch(self.keyword[1])
		intersection = set(cursor1).intersection(cursor2)
		if intersection == []:
			if cursor1:
				return cursor1
			elif cursor2:
				return cursor2
			else:
				return []

		for i in self.keyword[2:]:
			cursor2 = self.KEMSearch(i)
			intersection = intersection.intersection(cursor2)
		return list(intersection)

	def incWeight(self, fullTitle):
		self.TitleAbbre.update({'key':self.keyword[0]}, {'$inc':{'value.{}'.format(fullTitle):1}}, upsert=True)