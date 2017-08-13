# -*- coding: utf-8 -*-
""" Created by Mevlana Ayas on 23.07.2017 """
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from teamroles.models import AuditMixin, Team
__author__ = 'mevlanaayas'


class User(AbstractUser, AuditMixin):
    pwd_must_change = models.BooleanField(_('pwd must change'), default=False)

    # 0 -> disabled by another user
    # 1 -> enabled by another user
    # 2 -> disabled due to password expire (won't do until further notice)
    # 3 -> disabled due to many login attempts in given interval
    # 4 -> auto enabled by server if activate user setting is true
    # 5 -> disabled due to not logged in for given interval
    # 6 -> auto enabled when reset password operation completed by disabled user

    disable_reason = models.IntegerField(_("Disable Reason"), blank=True, null=True)

    class Meta(object):
        unique_together = ('email',)
        db_table = 'django_teams_user'

    def team(self):
        team = Team.objects.get(userteam__user=self)
        return team

    def teammates(self):
        team = self.team()
        teammates = User.objects.filter(userteam__team=team)
        return teammates

# bu iki methodla guardianın yaptığı işi daha kolay hale getirmeliyim.
    #  kodlamadan permission eklemek ve kontrol etmek gibi
    #  ve bütün modeller için kullanabilmenin bir yolunu bulsam iyi olabilir

    def perm_exists(self):
        pass

    def add_perm(self):
        pass
