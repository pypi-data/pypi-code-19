#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import re, jieba, pyprind, pymongo, json, jieba
from timetable.models import Course
from collections import defaultdict

class Command(BaseCommand):
	help = 'Convenient Way to insert Course json into Mongo and DB of Django'
	client = pymongo.MongoClient(None)
	db = client['timetable']
	Genra = db['Genra']
	CourseOfDept = db['CourseOfDept']
	CourseOfTime = db['CourseOfTime']
	CourseSearch = db['CourseSearch']
	timeTable = {
		'1':{'0':defaultdict(set),'1':defaultdict(set),'2':defaultdict(set),'3':defaultdict(set),'4':defaultdict(set),'5':defaultdict(set),'6':defaultdict(set),'7':defaultdict(set),'8':defaultdict(set),'9':defaultdict(set),'10':defaultdict(set),'11':defaultdict(set),'12':defaultdict(set),'13':defaultdict(set)},
		'2':{'0':defaultdict(set),'1':defaultdict(set),'2':defaultdict(set),'3':defaultdict(set),'4':defaultdict(set),'5':defaultdict(set),'6':defaultdict(set),'7':defaultdict(set),'8':defaultdict(set),'9':defaultdict(set),'10':defaultdict(set),'11':defaultdict(set),'12':defaultdict(set),'13':defaultdict(set)},
		'3':{'0':defaultdict(set),'1':defaultdict(set),'2':defaultdict(set),'3':defaultdict(set),'4':defaultdict(set),'5':defaultdict(set),'6':defaultdict(set),'7':defaultdict(set),'8':defaultdict(set),'9':defaultdict(set),'10':defaultdict(set),'11':defaultdict(set),'12':defaultdict(set),'13':defaultdict(set)},
		'4':{'0':defaultdict(set),'1':defaultdict(set),'2':defaultdict(set),'3':defaultdict(set),'4':defaultdict(set),'5':defaultdict(set),'6':defaultdict(set),'7':defaultdict(set),'8':defaultdict(set),'9':defaultdict(set),'10':defaultdict(set),'11':defaultdict(set),'12':defaultdict(set),'13':defaultdict(set)},
		'5':{'0':defaultdict(set),'1':defaultdict(set),'2':defaultdict(set),'3':defaultdict(set),'4':defaultdict(set),'5':defaultdict(set),'6':defaultdict(set),'7':defaultdict(set),'8':defaultdict(set),'9':defaultdict(set),'10':defaultdict(set),'11':defaultdict(set),'12':defaultdict(set),'13':defaultdict(set)},
		'6':{'0':defaultdict(set),'1':defaultdict(set),'2':defaultdict(set),'3':defaultdict(set),'4':defaultdict(set),'5':defaultdict(set),'6':defaultdict(set),'7':defaultdict(set),'8':defaultdict(set),'9':defaultdict(set),'10':defaultdict(set),'11':defaultdict(set),'12':defaultdict(set),'13':defaultdict(set)},
		'7':{'0':defaultdict(set),'1':defaultdict(set),'2':defaultdict(set),'3':defaultdict(set),'4':defaultdict(set),'5':defaultdict(set),'6':defaultdict(set),'7':defaultdict(set),'8':defaultdict(set),'9':defaultdict(set),'10':defaultdict(set),'11':defaultdict(set),'12':defaultdict(set),'13':defaultdict(set)}
	}
	semester = None
	school = None
	
	def add_arguments(self, parser):
		# Positional arguments
		parser.add_argument('course', type=str)
		parser.add_argument('school', type=str)
		parser.add_argument('semester', type=str)

	def handle(self, *args, **options):
		self.school = options['school']
		self.semester = options['semester']
		course = json.load(open(options['course'], 'r'))
		self.main(course)

		self.stdout.write(self.style.SUCCESS('crawl Job Json success!!!'))

	def main(self, jsonFile):
		GenraTable = defaultdict(dict)
		CourseOfDeptTable = defaultdict(dict)
		CourseSearchTable = defaultdict(set)
		uniqueCodeSet = set()
		CourseList = [] # waiting to insert into django DB.

		for course in pyprind.prog_bar(jsonFile):
			self.forGenra(course, GenraTable)
			self.forDept(course, CourseOfDeptTable)
			self.forTime(course)

			if course['code'] not in uniqueCodeSet:
				uniqueCodeSet.add(course['code'])				
				CourseList.append(self.json2django(course))
				self.BuildIndex(CourseSearchTable, course)

		self.CourseSearch.remove({'school':self.school})
		self.CourseSearch.insert(tuple( {'key':key, 'school':self.school, 'value':list(value)} for key, value in CourseSearchTable.items() if key != '' and key!=None))
		self.CourseSearch.create_index([("key", pymongo.ASCENDING), ("school", pymongo.ASCENDING)])

		Course.objects.filter(school=self.school).delete()
		Course.objects.bulk_create(CourseList)

		self.sortGenra(GenraTable)
		self.Genra.update_one({'school':self.school},{'$set': {'school':self.school, 'Genra':GenraTable}}, upsert=True)
		self.Genra.create_index([("school", pymongo.HASHED)])

		self.CourseOfDept.update_one({'school':self.school},{'$set': {'school':self.school, 'CourseOfDept':CourseOfDeptTable}}, upsert=True)
		self.CourseOfDept.create_index([("school", pymongo.HASHED)])

		self.set2tuple()
		self.CourseOfTime.update_one({'school':self.school}, {'$set':{'school':self.school, 'CourseOfTime':self.timeTable}}, upsert=True)
		self.CourseOfTime.create_index([("school", pymongo.HASHED)])

	def forGenra(self, course, GenraTable):
		if course['category'] != '必修類' and course['category'] != '選修類':
			GenraTable[course['category']].setdefault(course['for_dept'], set()).add(course['grade'])
		else:
			GenraTable['大學部'].setdefault(course['for_dept'], set()).add(course['grade'])

	def forDept(self, course, CourseOfDeptTable):
		if course['obligatory_tf']:
			CourseOfDeptTable[course['for_dept']].setdefault('obligatory', {}).setdefault(course['grade'], []).append(course['code'])
		else:
			CourseOfDeptTable[course['for_dept']].setdefault('optional', {}).setdefault(course['grade'], []).append(course['code'])

	@staticmethod
	def sortGenra(GenraTable):
		sortingOrder = '01234567一二三四五六日ABCDEFGH'
		for g in GenraTable:
			for key, value in GenraTable[g].items():
				GenraTable[g][key] = sorted(list(value), key=lambda x:sortingOrder.index(x[0]))

	def forTime(self, course):
		for i in course['time']:
			day = i['day']
			for time in i['time']:
				try:
					if course['category'] != '必修類' and course['category'] != '選修類':
						self.timeTable[str(day)][str(time)][course['category']].add(course['code'])
					else:
						self.timeTable[str(day)][str(time)][course['for_dept']].add(course['code'])
				except Exception as e:
					print(course)
					raise e
	def set2tuple(self):
		for day in self.timeTable:
			for time in self.timeTable[day]:
				for codeList in self.timeTable[day][time]:
					self.timeTable[day][time][codeList] = tuple(self.timeTable[day][time][codeList])

	def json2django(self, course):
		time = ''
		for i in course['time']:
			time += str(i['day']) + '-'
			for j in i['time']:
				time += str(j) + '-'
			time = time[:-1]
			time += ','

		return ( 
			Course(
				school=self.school.upper(),
				semester=self.semester,
				code=course['code'],
				credits=course['credits'],
				title=course['title'],
				department=course['department'],
				professor=course['professor'],
				time=time[:-1],
				location=course['location'][0] if len(course['location']) else '',
				obligatory=course['obligatory_tf'],
				note=course['note'],
				discipline=course['discipline']
			)
		)


	@staticmethod
	def bigram(title):
		title = re.sub(r'\(.*\)', '', title.split(',')[0]).split()[0].strip()
		bigram = (title, )
		if len(title) > 2:
			prefix = title[0]
			for i in range(1, len(title)):
				if title[i:].count(title[i]) == 1:
					bigram += (prefix + title[i],)
		return bigram

	def BuildIndex(self, CourseSearchTable, course):
		key = self.bigram(course['title'])
		titleTerms = (i for i in jieba.cut(course['title']) if len(i)>=2)
		CourseCode = course['code']

		for k in key:
			CourseSearchTable[k].add(CourseCode)
		for t in titleTerms:
			CourseSearchTable[t].add(CourseCode)
		CourseSearchTable[course['professor']].add(CourseCode)
		CourseSearchTable[CourseCode].add(CourseCode)