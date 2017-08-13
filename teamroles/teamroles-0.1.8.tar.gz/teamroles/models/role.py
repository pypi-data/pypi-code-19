# -*- coding: utf-8 -*-
""" Created by Mevlana Ayas on 22/07/2017 """
from django.db import models
from django.utils.translation import ugettext_lazy as _
from teamroles.models.mixins import AuditMixin

__author__ = 'mevlanaayas'


class Role(AuditMixin):
    name = models.CharField(_('Role Name'), db_column='name', max_length=200, unique=True)
    status = models.BooleanField(default=True)
    next_role = models.ForeignKey('self',
                                  verbose_name=_('Next Role'),
                                  db_column='next_role',
                                  related_name='next_step',
                                  null=True,
                                  blank=True,
                                  on_delete=models.SET_NULL,
                                  default=None)
    previous_role = models.ForeignKey('self',
                                      verbose_name=_('Previous Role'),
                                      db_column='previous_role',
                                      related_name='previous_step',
                                      null=True,
                                      blank=True,
                                      on_delete=models.SET_NULL,
                                      default=None)

    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        db_table = 'django_teams_role'
        app_label = 'teamroles'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class AbstractRole(AuditMixin):
    name = models.CharField(_('Role Name'), db_column='name', max_length=200, unique=True)
    status = models.BooleanField(default=True)

    class Meta:
        abstract = True
