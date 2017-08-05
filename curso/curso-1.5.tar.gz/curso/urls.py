# -*- coding: utf-8 -*-
from django.conf.urls import url
from curso import views
urlpatterns = [
	url(r'^get/search/$', views.search, name='search'),
	url(r'^post/incWeight/$', views.incWeight, name='incWeight'),
]