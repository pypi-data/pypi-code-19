from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^headers/$', views.index, name='home'),
    url(r'^login/$', views.token, name='kong_login'),
]