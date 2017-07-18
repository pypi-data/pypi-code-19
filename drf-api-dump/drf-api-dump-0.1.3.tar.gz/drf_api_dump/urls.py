from django.conf.urls import url

from .views import DrfDumpApiView

urlpatterns = [
    url(r'^(?P<pk>.+)/{0,1}$', DrfDumpApiView.as_view(), name='dump-app-view'),
    url(r'^', DrfDumpApiView.as_view(), name='dump-app-view'),
]