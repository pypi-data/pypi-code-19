from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$',
        view=views.environments_view,
        name='api_environments'),

    url(r'^(?P<environment>\w+)/$',
        view=views.components_view,
        name='api_components'),

    url(r'^(?P<environment>\w+)/(?P<alias>[-\w\d]+)/$',
        view=views.component_settings_view,
        name='api_component'),
]
