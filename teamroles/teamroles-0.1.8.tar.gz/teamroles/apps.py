# -*- coding: utf-8 -*-
""" Created by Mevlana Ayas on 23.07.2017 """
from __future__ import unicode_literals, absolute_import
from django.apps import AppConfig
import logging
from django.utils.translation import ugettext_lazy as _

__author__ = 'mevlanaayas'


class TeamrolesConfig(AppConfig):
    """ Common app configuration. """
    name = 'teamroles'
    label = 'teamroles'
    verbose_name = _("Role Base Management Apps for Teams")

    def ready(self):
        logging.debug("Importing %s related services...", self.verbose_name)
        logging.debug("Done!")
