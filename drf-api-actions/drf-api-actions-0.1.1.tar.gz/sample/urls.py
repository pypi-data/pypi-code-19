from django.conf.urls import include, url

from sample import settings
from sample.views import UsersAPIView, UsersActionReadAPIView, UsersExtraFieldsAPIView

urlpatterns = [
    url('^api', include([
        url('^users$', UsersAPIView.as_view()),
        url('^users-action-read$', UsersActionReadAPIView.as_view()),
        url('^users-extra-fields$', UsersExtraFieldsAPIView.as_view()),
    ])),
]

if settings.DEBUG:
    urlpatterns += [
        url('^', include('drf_api_actions.urls'))
    ]
