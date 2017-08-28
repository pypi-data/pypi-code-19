# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings


def make_link(url, label, icon, id=None, classes=None):
    """make a link"""
    icon_url = settings.STATIC_URL + icon
    
    extra_args = ['id="{0}"'.format(id)] if id else []
    if classes:
        extra_args += ['class="{0}"'.format(' '.join(classes))]
        
    return '<a href="{url}" style="background-image:url({icon_url})" {args}>{label}</a>'.format(
        url=url, icon_url=icon_url, args=' '.join(extra_args), label=label
    )


def context_to_dict(context):
    """convert a django context to a dict"""
    the_dict = {}
    for elt in context:
        the_dict.update(dict(elt))
    return the_dict