# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Picture(models.Model):
    identificador = models.CharField(max_length=100)
    url = models.URLField()
    creado_en = models.DateTimeField(
        auto_now_add=True
    )
    modificado_en = models.DateTimeField(
        auto_now=True
    )

    def __unicode__(self):
        return u"{}".format(
            self.identificador
        )
