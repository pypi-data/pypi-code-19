# coding: utf-8

from django.conf.urls import url

from djotali.contacts import views

app_name = 'contacts-groups'
urlpatterns = [
    url(r'^$', views.ContactsGroupsIndexView.as_view(), name='index'),
    url(r'^new$', views.CreateContactsGroupsView.as_view(), name='new'),
    url(r'^(?P<pk>\d+)$', views.ShowContactsGroupView.as_view(), name='show'),
    url(r'^(?P<pk>\d+)/edit$', views.EditContactsGroupView.as_view(), name='edit'),
    url(r'^(?P<pk>\d+)/delete$', views.DeleteContactsGroupView.as_view(), name='delete'),
]
