from django.conf.urls import url

from configfactory.configurations import views

urlpatterns = [
    url(r'^components/create/$', view=views.component_create, name='new_component'),
    url(r'^components/(?P<alias>[-\w\d]+)/$', view=views.component_view, name='view_component'),
    url(r'^components/(?P<alias>[-\w\d]+)/edit/$',
        view=views.component_edit, name='edit_component'),
    url(r'^components/(?P<alias>[-\w\d]+)/edit/schema/$', view=views.component_edit_schema,
        name='edit_component_schema'),
    url(r'^components/(?P<alias>[-\w\d]+)/delete/$',
        view=views.component_delete, name='delete_component'),
    url(r'^components/(?P<alias>[-\w\d]+)/(?P<environment>\w+)/$', view=views.component_view,
        name='view_component_by_env'),
]
