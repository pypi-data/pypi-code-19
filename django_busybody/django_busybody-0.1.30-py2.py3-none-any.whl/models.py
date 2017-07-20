# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import json
import time

from django.conf import settings
from django.db import IntegrityError
from django.db import transaction
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.fields.files import FieldFile
from future.utils import python_2_unicode_compatible

from . import tools


@python_2_unicode_compatible
class History(models.Model):

    """
    object change history
    """
    target_type = models.ForeignKey(ContentType)
    target_object_id = models.PositiveIntegerField()
    target = GenericForeignKey(
        'target_type', 'target_object_id')
    who = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.PROTECT)
    uri = models.CharField(max_length=512, blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    changes = models.TextField()

    @classmethod
    def serialize_field(self, value):
        if isinstance(value, FieldFile):
            return value.url
        elif isinstance(value, models.Model):
            klass = value.__class__
            return '{}.{}({})'.format(klass.__module__, klass.__name__, value.pk)
        return repr(value)

    @classmethod
    def _on_change(klass, includes, excludes, sender, instance, **kwargs):
        if not instance.pk or kwargs.get('created'):
            return
        old = instance.__class__.objects.get(pk=instance.pk)
        d = {}
        for f in instance.__class__._meta.get_fields():
            if includes and f.name not in includes:
                continue
            if excludes and f.name in excludes:
                continue
            n = getattr(instance, f.name)
            o = getattr(old, f.name)
            if n != o:
                d[f.name] = klass.serialize_field(o), klass.serialize_field(n)
        if d:
            who, uri = tools.get_global_request('user'), tools.get_global_request('path')
            klass.objects.create(
                target=instance, who=who, uri=uri, changes=json.dumps(d))

    @classmethod
    def on_change(klass, instance, includes=None, excludes=None, created=False):
        return klass._on_change(None, includes, excludes, None, instance, created=created)


@python_2_unicode_compatible
class EmailCategory(models.Model):

    """
    Model to store email category
    """
    name = models.CharField(max_length=256, unique=True)
    display_name = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name if self.display_name else self.name


@python_2_unicode_compatible
class EmailLog(models.Model):

    """
    Model to store all the outgoing emails.
    """

    when = models.DateTimeField(null=False, auto_now_add=True)
    to = models.EmailField(null=False, blank=False)
    from_email = models.EmailField(null=False, blank=False)
    subject = models.TextField(null=False)
    body = models.TextField(null=False)
    user_id = models.IntegerField(default=0)
    ok = models.BooleanField(null=False, default=True)
    stack_trace = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=256, blank=True, null=True)
    message_id = models.CharField(max_length=1024, blank=True, null=True)
    request_id = models.CharField(max_length=1024, blank=True, null=True)
    category = models.ForeignKey(EmailCategory, blank=True, null=True)

    bounced = models.BooleanField(null=False, default=False)
    complained = models.BooleanField(null=False, default=False)
    delivered = models.BooleanField(null=False, default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class _EmailLoggerSetAttr(object):

    def __init__(self, attr_name):
        self.attr_name = attr_name

    def __call__(self, sender, instance, **kwargs):
        if not kwargs['created']:
            return
        for email in EmailLog.objects.filter(message_id=instance.mail_id):
            setattr(email, self.attr_name, True)
            email.save()


class LockError(Exception):
    pass


@python_2_unicode_compatible
class NaiveLock(models.Model):
    lock_id = models.CharField(max_length=256, unique=True)
    when_acquired = models.FloatField()
    when_expired = models.FloatField()

    @classmethod
    def acquire(klass, lock_id, timeout=1, lock_time=60, sleep_time=0.1):
        et = klass.get_current_time() + timeout
        ct = klass.get_current_time()
        while ct < et:
            try:
                klass.objects.filter(when_expired__lt=ct).delete()
                with transaction.atomic():
                    return klass.objects.create(
                        lock_id=lock_id,
                        when_acquired=ct,
                        when_expired=ct + lock_time,
                    )
            except IntegrityError:
                if sleep_time <= 0:
                    break
                time.sleep(sleep_time)
                ct = klass.get_current_time()
                continue
        raise LockError('timeout')

    @classmethod
    def get_current_time(klass):
        return time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tbl):
        self.delete()


try:
    import django_bouncy  # NOQA
    __cbs = []
    for attr, model_name in [('delivered', 'Delivery'), ('bounced', 'Bounce'), ('complained', 'Complaint')]:
        cb = _EmailLoggerSetAttr(attr)
        models.signals.post_save.connect(
            cb, 'django_bouncy.{}'.format(model_name),
            dispatch_uid='django_busybody.rules._set_{}'.format(attr))
        __cbs.append(cb)
except ImportError:  # pragma: no cover
    pass
