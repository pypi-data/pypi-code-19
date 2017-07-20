from django.conf.urls import url

from . import example

urlpatterns = [
    url(r'^example/sendmail', example.sendmail),
]
