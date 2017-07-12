from django.conf.urls import url, include
from django.views import generic

from npolling import views

urlpatterns = [
    # url('^$', include(views.ComparisonReportViewSet().urls)),
    # url('^$', views.ComparisonReportListView.as_view(), name='index'),
    url('^$', generic.TemplateView.as_view(template_name="npolling/index.html"), name="index"),
    # url('^$', views.index, name="index")

]
