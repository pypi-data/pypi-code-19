# -*- coding: utf-8 -*-
""" Created by Mevlana Ayas on 23.07.2017 """
from __future__ import unicode_literals
from django.http import HttpResponse
from guardian.models import Permission
from django.contrib.contenttypes.models import ContentType
__author__ = 'mevlanaayas'


# bunların daha user friendly olması için app_label ya da model gibi parametreleri daha açık bir şekilde sun.
def add(name="Can Deneme", codename='deneme', app_label='teamroles', model='Team'):
    content_type = ContentType.objects.get(app_label=app_label.lower(), model=model.lower())
    content_type_id = content_type.id
    new_permission = Permission.objects.create(content_type_id=content_type_id, name=name, codename=codename)
    return HttpResponse("Text only, please.", content_type="text/plain")
