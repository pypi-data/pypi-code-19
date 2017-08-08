# -*- coding: utf-8 -*-
from django.conf.urls import url
from curso import views
urlpatterns = [
	url(r'^$', views.search, name='search'),
	url(r'^incWeight/$', views.incWeight, name='incWeight'),
]