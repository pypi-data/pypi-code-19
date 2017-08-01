from django.conf.urls import url
from django.contrib import admin
from django_pre_post.views import FillOutQuestionnaire, FramelessQuestionnaire
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^questionnaire/(?P<pk>\d+)/$', FillOutQuestionnaire.as_view(), name='fill-out-questionnaire'),
    url(r'^success/',
        TemplateView.as_view(template_name='django_pre_post/successful_post.html'),
        name='successful-submission'),
    url(r'^embed-questionnaire/(?P<pk>\d+)/$', FramelessQuestionnaire.as_view(), name='embed-questionnaire'),
]
