# coding: utf-8

from django.conf.urls import url

from djotali.contacts import views

app_name = 'contacts'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^new$', views.CreateContactView.as_view(), name='new'),
    url(r'^edit/(?P<pk>\d+)$', views.EditContactView.as_view(), name='edit'),
    url(r'^delete/(?P<pk>\d+)$', views.DeleteContactView.as_view(), name='delete'),
]
