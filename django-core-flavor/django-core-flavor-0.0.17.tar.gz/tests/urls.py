from django.conf.urls import include
from django.conf.urls import url

urlpatterns = [
    url(r'^auth/', include(
        'rest_framework.urls',
        namespace='rest_framework')),

    url(r'^v1/', include('tests.api.urls', namespace='v1')),
    url(r'^(v2/)?', include('tests.api.urls', namespace='v2')),
]
