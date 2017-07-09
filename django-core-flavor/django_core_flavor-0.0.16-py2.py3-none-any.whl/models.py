import uuid

from pathlib import Path

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel

from . import managers


@deconstructible
class UUIDUploadTo(object):

    def __init__(self, path):
        self.path = Path(path)

    def __call__(self, instance, filename):
        return timezone.now().strftime((
            self.path / (uuid.uuid4().hex + Path(filename).suffix)
        ).as_posix())


class ContentTypeModel(models.Model):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        verbose_name=_('content type'))

    object_id = models.CharField(
        db_index=True,
        max_length=64,
        verbose_name=_('content ID'))

    class Meta:
        abstract = True


class SoftDeletableModel(models.Model):
    removed = models.DateTimeField(_('removed'), blank=True, null=True)
    objects = managers.SoftDeletableManager()

    class Meta:
        abstract = True

    def delete(self, soft=True):
        if soft:
            self.removed = timezone.now()
            self.save()
        else:
            super().delete()


class TimeStampedUUIDModel(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)

    class Meta:
        abstract = True
