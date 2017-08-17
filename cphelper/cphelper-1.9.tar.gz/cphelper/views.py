# -*- coding: utf-8 -*-
from django.http import JsonResponse
from djangoApiDec.djangoApiDec import queryString_required
from pymongo import MongoClient

class Course(object):
	"""docstring for Course"""
	def __init__(self, school, uri=None):
		self.school = school
		self.db = MongoClient(uri)['timetable']

	@staticmethod
	def Cursor2Dict(cursor):
		if cursor.count() == 0:
			return {}
		return list(cursor)[0]

	def getByDept(self, dept, grade=None):
		if grade == None:
			CourseDict = self.Cursor2Dict(self.db['CourseOfDept'].find({"school":self.school}, {'_id':False, 'CourseOfDept.{}'.format(dept):1}).limit(1))
		else:
			CourseDict = self.Cursor2Dict(self.db['CourseOfDept'].find({'school':self.school}, {'_id':False, 'CourseOfDept.{}.optional.{}'.format(dept, grade):1, 'CourseOfDept.{}.obligatory.{}'.format(dept, grade):1}).limit(1))
		return CourseDict['CourseOfDept'][dept]

	def getByTime(self, day, time, deptArr):
		CourseDict = []
		tmp = self.Cursor2Dict(self.db['CourseOfTime'].find({'school':self.school}, {'CourseOfTime.{}.{}'.format(day, time):1, '_id':False}).limit(1))['CourseOfTime'][day][time]
		for dept in deptArr:
			if dept in tmp:
				CourseDict += tmp[dept]
		return CourseDict

	def getGenra(self):
		return self.Cursor2Dict(self.db['Genra'].find({"school" : self.school}, {'Genra':1, '_id':False}))['Genra']

@queryString_required(['dept', 'school'])
def CourseOfDept(request):
	"""
		Generate list of obligatory and optional course of specific Dept.
	"""
	dept = request.GET['dept']
	school = request.GET['school']
	c = Course(school=school)
	return JsonResponse(c.getByDept(dept=dept, grade=request.GET['grade'] if 'grade' in request.GET else None), safe=False)

@queryString_required(['day', 'time', 'school', 'dept'])
def CourseOfTime(request):
	"""
		Generate list of obligatory and optional course of specific Dept.
	"""
	day = request.GET['day']
	time = request.GET['time']
	school = request.GET['school']
	dept = request.GET['dept'].split()
	c = Course(school=school)
	return JsonResponse(c.getByTime(day=day, time=time, deptArr=dept), safe=False)

@queryString_required(['school'])
def Genra(request):
	"""
		Generate dict of Dept and its grade.
	"""
	school = request.GET['school']
	c = Course(school=school)
	return JsonResponse(c.getGenra(), safe=False)
