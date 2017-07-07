# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
from datetime import datetime
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.sitemaps import Sitemap
from django.core.exceptions import ObjectDoesNotExist

from .models import Term

logger = logging.getLogger(__name__)


class GlossarioSitemap(Sitemap):
    MINDATE = datetime(2010, 2, 22)

    @classmethod
    def get_content_type(cls):
        return ContentType.objects.get_by_natural_key(app_label='glossario', model='term')

    def __init__(self, cutoff=None, *args, **kwargs):
        super(GlossarioSitemap, self).__init__()
        self.queryset = LogEntry.objects.filter(content_type=self.get_content_type())
        self.cutoff = cutoff

    def items(self):
        return Term.objects.filter(alias__isnull=True).order_by('name')

    def location(self, item):
        return item.get_url()

    def lastmod(self, item):
        try:
            return self.queryset.filter(object_id=item.pk).latest('action_time').action_time
        except ObjectDoesNotExist:
            pass
        except:
            logger.exception("{} lastmod error".format(self.__class__.__name__))
        return self.MINDATE

    priority = 0.6
    changefreq = 'weekly'
