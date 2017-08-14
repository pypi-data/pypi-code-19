from django.conf.urls import url

from .views import FeedView

app_name = 'flashbriefing'
urlpatterns = [
    url(r'^feeds/(?P<uuid>\w+).(?P<format>\w+)$',
        FeedView.as_view(), name='feed'),
]
