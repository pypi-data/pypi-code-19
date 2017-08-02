# -*- coding: utf-8 -*-
from django.conf.urls import url, include

from threebot_hook import views

urlpatterns = [
    url(r'^list/(?P<wf_slug>[\w-]+)/$', views.hooks_list, name='hook_list'),
    url(r'^create/(?P<wf_slug>[\w-]+)/$', views.create, name='hook_create'),
    url(r'^edit/(?P<wf_slug>[\w-]+)/(?P<hook_slug>[\w-]+)/$', views.edit, name='hook_edit'),
    url(r'^(?P<token>[\w-]+)/(?P<identifier>[\w-]+)/$', views.HookView.as_view()),
]
