from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.articles_view, name='articles'),
    url(r'^(?P<article_slug>[\d\w\-]+)/$', views.article_view, name='article'),
]
