"""
Generally, each wiki on a website will want its own set of URLs. These can be
created in a Django URL conf using the :func:`include_wiki` function, which
produces a set of URLs for the given wiki namespace. 
"""

from django.conf import settings
from django.conf.urls import include, url
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse_lazy
from django.utils.text import slugify
from thorson_wiki import views

import django.contrib.auth.views as auth_views

def include_wiki(namespace_):
    """
    :param namespace_: the name of the wiki to include
    :rtype namespace_: str

    Creates a set of URLs for the given namespace. This is used much like
    :func:`django.conf.urls.include`, except it is given a string, which should
    correspond to a namespace your settings.
    """

    if namespace_ not in getattr(settings, 'THORSONWIKI_NAMESPACES', {}):
        raise ImproperlyConfigured(("Included namespace '%s' not in" \
                " Django settings.") % namespace_)

    return include((generate_urls(namespace_), 'thorson_wiki'), namespace_)

def generate_urls(namespace_):
    """
    Returns a list of URLs for the given namespace.
    """

    namespaces = getattr(settings, 'THORSONWIKI_NAMESPACES', {})

    try:
        namespace = namespaces[namespace_]
    except KeyError:
        raise ImproperlyConfigured("Invalid namespace: '%s'" % namespace_)

    templates = namespace.get('templates', {})
    login_template = templates.get('login', 'thorson_wiki/login.html')
    password_change_template = templates.get('password_change',
            'thorson_wiki/password_change.html')
    password_reset_template = templates.get('password_reset',
            'thorson_wiki/password_reset.html')
    password_reset_confirm_template = templates.get('password_reset_confirm',
            'thorson_wiki/password_reset_confirm.html')

    landing_page = slugify(
            namespace.get('landing', namespaces.get('title', 'Main page'))
    )

    return [
        # Landing page
        url(r'^$', views.article_detail,
            {'namespace_': namespace_, 'slug': landing_page}, name='main'),

        # Authentication
        url(r'^user/login/$', auth_views.login,
            {'template_name': login_template, 'extra_context': {'namespace_':
                namespace_, 'namespace': namespace}}, name='login'),
        url(r'^user/logout/$', auth_views.logout, name='logout'),
        url(r'^user/password_change/$', auth_views.password_change,
            {'template_name': password_change_template, 'extra_context':
                {'namespace_': namespace_, 'namespace': namespace}},
            name='password_change'),
        url(r'^user/password_reset/$', auth_views.password_reset,
            {'template_name': password_reset_template, 'extra_context':
                {'namespace_': namespace_, 'namespace': namespace}}),
        url(r'^user/password_confirm/$', auth_views.password_reset_confirm,
            {'template_name': 'thorson_wiki/password_reset_confirm.html',
                'extra_context': {'namespace_': namespace_, 'namespace':
                    namespace}},
            name='password_reset_confirm'),

        # User info
        url(r'^user/register/$', views.register, {'namespace_': namespace_},
            name='user_create'),
        url(r'^user/update/$', views.user_update, {'namespace_': namespace_},
            name='user_update'),

        # Search
        url(r'^search/$', views.search, {'namespace_': namespace_},
            name='search'),

        # Articles
        url(r'^article/read/(?P<slug>[a-zA-Z0-9-_]+)/$',
             views.article_detail, {'namespace_': namespace_},
             name='article'),
        url(r'^article/update/(?P<slug>[a-zA-Z0-9-_]+)/$',
            views.article_update, {'namespace_': namespace_},
            name='article_update'),
        url(r'^article/delete/(?P<slug>[a-zA-Z0-9-_]+)/$',
            views.article_delete, {'namespace_': namespace_},
            name='article_delete'),
        url(r'^article/create/$', views.article_create,
            {'namespace_': namespace_}, name='article_create'),
        url(r'^article/list/$', views.article_list,
             {'namespace_': namespace_}, name='article_list'),
    ]
