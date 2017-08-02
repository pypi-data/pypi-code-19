from __future__ import absolute_import, unicode_literals

from uuid import uuid4
from django.db import models
from django.conf import settings


class AuthToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='auth_tokens', on_delete=models.CASCADE
    )
    device_id = models.CharField(max_length=255)

    token = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid4().hex

        super(AuthToken, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'device_id')
