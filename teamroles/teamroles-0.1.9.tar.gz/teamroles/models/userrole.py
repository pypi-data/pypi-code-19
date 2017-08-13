# -*- coding: utf-8 -*-
""" Created by Mevlana Ayas on 22.07.2017 """
from django.db import models
from django.utils.translation import ugettext_lazy as _
from teamroles.models import AuditMixin
from teamroles.models.user import User
from teamroles.models.role import Role

__author__ = 'mevlanaayas'


class UserRole(AuditMixin):
    user = models.ForeignKey(User, verbose_name=_('User'), db_column='user')
    role = models.ForeignKey(Role, verbose_name=_('Role'), db_column='role')

    class Meta:
        unique_together = ("user", "role")
        verbose_name = _('User role')
        verbose_name_plural = _('User roles')
        db_table = 'django_teams_user_roles'
        app_label = 'teamroles'

    def __unicode__(self):
        return self.user.username + " has role, " + str(self.role.name)

    def __str__(self):
        return self.user.username + " has role, " + str(self.role.name)
