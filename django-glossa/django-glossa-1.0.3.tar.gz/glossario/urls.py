# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.conf.urls import patterns, url
from django.views.generic import RedirectView

from . import views

urlpatterns = patterns(
    '',
    url(r'^$', RedirectView.as_view(pattern_name='glossario_index', permanent=True), kwargs={'current': 'a'}, name='glossario'),
    url(r'^(?P<current>[a-z])/$', views.TermListView.as_view(), name='glossario_index'),
    # url(r'^(?P<current>[A-Z])/$', views.TermListView.as_view(), name='glossario_index'),
    url(r'^(?P<current>[a-z])/(?P<pk>[-a-z0-9]+)/$', views.TermDetailView.as_view(), name='glossario_term'),
    # url(r'^(?P<current>[a-zA-Z])/(?P<pk>[-a-zA-Z0-9]+)/$', views.TermDetailView.as_view(), name='glossario_term'),
)
