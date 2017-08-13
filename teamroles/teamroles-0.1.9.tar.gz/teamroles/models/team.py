# -*- coding: utf-8 -*-
""" Created by Mevlana Ayas on 22.07.2017 """
from django.db import models
from django.utils.translation import ugettext_lazy as _
from teamroles.models import AuditMixin

__author__ = 'mevlanaayas'


class Team(AuditMixin):
    name = models.CharField(_('Name'), db_column='name', max_length=100)
    code_name = models.CharField(_('Codename'), db_column='codename', max_length=100, unique=True)

    class Meta:
        unique_together = (("name", "code_name"), )
        verbose_name = _('Team')
        verbose_name_plural = _('Teams')
        db_table = 'django_teams_team'
        app_label = 'teamroles'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class AbstractTeam(AuditMixin):
    name = models.CharField(_('Name'), db_column='name', max_length=100)
    code_name = models.CharField(_('Codename'), db_column='codename', max_length=100, unique=True)

    class Meta:
        abstract = True
