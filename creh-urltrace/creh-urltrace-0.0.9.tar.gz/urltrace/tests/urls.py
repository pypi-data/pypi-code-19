from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^url_trace3/$', views.empty, name='url_trace3'),
]