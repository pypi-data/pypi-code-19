# -*- coding: utf-8 -*-
""" Created by Mevlana Ayas on 22/07/2017 """
from django.db import models
from django.utils.translation import ugettext_lazy as _
from teamroles.models.mixins import AuditMixin

__author__ = 'mevlanaayas'


class Role(AuditMixin):
    name = models.CharField(_('Role Name'), db_column='name', max_length=200, unique=True)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        db_table = 'django_teams_role'
        app_label = 'teamroles'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

