# -*- coding: utf-8 -*-
from django.http import JsonResponse
from djangoApiDec.djangoApiDec import queryString_required
from pymongo import MongoClient

class Course(object):
	"""docstring for Course"""
	def __init__(self, school, uri=None):
		self.school = school
		self.db = MongoClient(uri)['timetable']

	def Cursor2Dict(self, cursor):
		if cursor.count() == 0:
			return {}
		return list(cursor)[0]

	def getByDept(self, dept, grade=None):
		if grade == None:
			CourseDict = self.Cursor2Dict(self.db['CourseOfDept'].find({ "$and":[{"school":self.school}, {'dept':dept}] },{'_id':False}).limit(1))
		else:
			CourseDict = self.Cursor2Dict(self.db['CourseOfDept'].find({ "$and":[{"school":self.school}, {'dept':dept}] },{'_id':False, 'course.optional.'+grade:1, 'course.obligatory.'+grade:1}).limit(1))
		return CourseDict['course']

	def getByTime(self, day, time, degreeArr, deptArr):
		CourseDict = []
		tmp = self.Cursor2Dict(self.db['CourseOfTime'].find({'school':self.school, 'day':int(day), 'time':int(time)}, {'value':1, '_id':False}).limit(1))
		for degree, dept in zip(degreeArr, deptArr):
			if degree in tmp['value'] and dept in tmp['value'][degree]:
				CourseDict += tmp['value'][degree][dept]
		return CourseDict

@queryString_required(['dept', 'school'])
def CourseOfDept(request):
	"""
		Generate list of obligatory and optional course of specific Dept.
	"""
	dept = request.GET['dept']
	school = request.GET['school']
	c = Course(school=school)
	return JsonResponse(c.getByDept(dept=dept, grade=request.GET['grade'] if 'grade' in request.GET else None), safe=False)

@queryString_required(['day', 'time', 'school', 'degree', 'dept'])
def TimeOfCourse(request):
	"""
		Generate list of obligatory and optional course of specific Dept.
	"""
	day = request.GET['day']
	time = request.GET['time']
	school = request.GET['school']
	degree = request.GET['degree'].split()
	dept = request.GET['dept'].split()
	c = Course(school=school)
	return JsonResponse(c.getByTime(day=day, time=time, degreeArr=degree, deptArr=dept), safe=False)
