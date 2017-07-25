# -*- coding: utf-8 -*-
from . import constants
from django.db import models
from django.utils import timezone


class UrlTraceGroup(models.Model):

    group_name = models.TextField(
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.SmallIntegerField(
        choices=constants.STATUS_CHOICES,
        default=constants.STATUS_TRUE
    )

    created_at = models.DateTimeField(
        default=timezone.now(),
        editable=False,
    )

    updated_at = models.DateTimeField(
        default=timezone.now(),
        editable=False,
    )

    def __str__(self):
        return "({}) {}".format(self.is_permanent, self.group_name)


class UrlTrace(models.Model):

    url_trace = models.TextField(unique=True)

    url_trace_group = models.ForeignKey(UrlTraceGroup)

    description = models.TextField(
        blank=True,
    )

    is_active = models.SmallIntegerField(
        choices=constants.STATUS_CHOICES,
        default=constants.STATUS_TRUE
    )

    created_at = models.DateTimeField(
        default=timezone.now(),
        editable=False,
    )

    updated_at = models.DateTimeField(
        default=timezone.now(),
        editable=False,
    )

    def __str__(self):
        return "({}) {}".format(self.is_permanent, self.group_name)


