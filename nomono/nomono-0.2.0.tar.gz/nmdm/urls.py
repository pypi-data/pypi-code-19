from django.conf.urls import url
from django.views import generic

from nmdm import views

urlpatterns = [

    url('^$', generic.TemplateView.as_view(template_name="nmdm/index.html"), name="index"),
    # url('^$', views.index, name="index")

]
