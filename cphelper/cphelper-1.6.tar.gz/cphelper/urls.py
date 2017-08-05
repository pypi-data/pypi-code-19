# -*- coding: utf-8 -*-
from django.conf.urls import url
from cphelper import views
urlpatterns = [
	url(r'^get/CourseOfDept/$', views.CourseOfDept, name='CourseOfDept'),
	url(r'^get/CourseOfTime/$', views.CourseOfTime, name='CourseOfTime'),
	url(r'^get/Genra/$', views.Genra, name='Genra'),
]