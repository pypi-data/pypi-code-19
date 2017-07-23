# -*- coding: utf-8 -*-
""" Created by Mevlana Ayas on 22.07.2017 """
from django.db import models
from django.utils.translation import ugettext_lazy as _
from teamroles.models import AuditMixin
from teamroles.models.team import Team
from teamroles.models.user import User

__author__ = 'mevlanaayas'


class UserTeam(AuditMixin):
    user = models.ForeignKey(User, verbose_name=_('User'), db_column='user')
    team = models.ForeignKey(Team, verbose_name=_('Team'), db_column='team')

    class Meta:
        unique_together = ("user", "team")
        verbose_name = _('User team')
        verbose_name_plural = _('User teams')
        db_table = 'django_teams_user_teams'
        app_label = 'teamroles'

    def __unicode__(self):
        return self.user.username + " in team of " + str(self.team.name)

    def __str__(self):
        return self.user.username + " in team of " + str(self.team.name)
