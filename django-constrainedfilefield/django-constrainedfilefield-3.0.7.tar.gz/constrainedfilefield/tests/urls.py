# -*- coding:utf-8 -*-
from django.conf.urls import url
from constrainedfilefield.tests import views

urlpatterns = [
    url(r'^nomodel/$', views.nomodel_form, name="nomodel"),
]
