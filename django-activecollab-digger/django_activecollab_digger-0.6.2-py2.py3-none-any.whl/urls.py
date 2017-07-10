from django.conf.urls import url

from .views import IndexPageView, tasks

urlpatterns = [
    url(r'^$', IndexPageView.as_view()),
    url(r'^tasks/$', tasks)
]
