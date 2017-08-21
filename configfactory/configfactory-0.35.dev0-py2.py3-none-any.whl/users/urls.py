from django.conf.urls import url
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^login/$',
        view=auth_views.login,
        name='login',
        kwargs={
            'template_name': 'login.html'
        }),

    url(r'^logout/$',
        view=auth_views.logout,
        name='logout',
        kwargs={
            'next_page': 'login'
        }),
]
