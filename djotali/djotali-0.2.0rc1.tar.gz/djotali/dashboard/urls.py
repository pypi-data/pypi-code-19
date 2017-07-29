# coding: utf8

from django.conf.urls import url

from djotali.dashboard import views

app_name = 'dashboard'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    # url(r'^(?P<message_id>[0-9]+)/$', views.IndexView.as_view(), name='index')
]
