from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', IndexPageView.as_view(), name='home'),
    url(r'^translate/$', translate, name=u'translate'),
]
