# -*- coding: utf-8 -*-
from __future__ import absolute_import
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class GlossarioApp(CMSApp):
    name = _("Glossario")
    urls = ["glossario.urls"]


apphook_pool.register(GlossarioApp)
