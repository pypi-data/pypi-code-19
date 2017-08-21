from django.conf.urls import url

from configfactory.auth import views

urlpatterns = [
    url(r'^login/$', view=views.login, name='login'),
    url(r'^logout/$', view=views.logout, name='logout'),
]
