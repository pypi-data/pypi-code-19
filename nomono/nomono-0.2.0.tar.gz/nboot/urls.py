from django.conf import settings
from django.conf.urls import include, url
from django.contrib import auth
from django.contrib.auth.models import User
from django.views import generic
from material.frontend import urls as frontend_urls

# urlpatterns = [
#     # url(r'^admin/', include(admin.site.urls)),
#     url(r'', include(frontend_urls)),
# ]

def users(request):
    return {
        'users': User.objects.filter(is_active=True).order_by('-username')
    }


urlpatterns = [
    # url(r'^accounts/login/$', auth.login, name='login'),
    # url(r'^accounts/logout/$', auth.logout, name='logout'),
    url(r'^$', generic.RedirectView.as_view(url='/workflow/', permanent=False)),
    # url('^$', generic.RedirectView.as_view(url='./npolling/', permanent=False), name="index"),
    url(r'', include(frontend_urls))
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls))
    ]
