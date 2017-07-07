from django.conf.urls import *

urlpatterns = patterns(
    'list2excel.views',
    url(r'^export/(?P<app_label>[a-z_]+)/(?P<model_name>[a-z_]+)/', 'export',
        name='list2excel'),
)
