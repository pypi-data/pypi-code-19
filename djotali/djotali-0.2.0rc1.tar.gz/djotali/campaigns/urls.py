# coding: utf8

from django.conf.urls import url, include

from djotali.campaigns import views
from djotali.campaigns.api import router

app_name = 'campaigns'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^new$', views.CreateView.as_view(), name='new'),
    url(r'^(?P<campaign_id>\d+)/notify$', views.campaign_notify, name='notify_campaign'),
    url(r'^(?P<pk>\d+)/notifications$', views.NotificationsView.as_view(), name='notifications'),
    url(r'^(?P<pk>\d+)$', views.DetailView.as_view(), name='show'),
    url(r'^(?P<pk>\d+)/edit$', views.EditView.as_view(), name='edit'),
    url(r'^(?P<campaign_id>\d+)/notifications/(?P<notification_id>\d+)/notify$', views.notify, name='core_notify'),
    # url(r'^(?P<message_id>[0-9]+)/$', views.IndexView.as_view(), name='index')
    url(r'^api/', include(router.urls, namespace='api_campaign'))
]
