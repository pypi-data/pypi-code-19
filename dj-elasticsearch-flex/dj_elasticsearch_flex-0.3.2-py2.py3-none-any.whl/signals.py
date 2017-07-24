import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from . import tasks
from .indexes import get_index_for_model

logger = logging.getLogger('elasticsearch_flex.signals')


@receiver(post_save)
def sync_elasticsearch_on_model_update_or_create(sender, instance, created, **kwargs):
    try:
        ix = get_index_for_model(sender)
    except KeyError:
        pass
    else:
        tasks.update_indexed_document.delay(ix, created, instance.pk)


@receiver(post_delete)
def sync_elasticsearch_on_model_delete(sender, instance, **kwargs):
    try:
        ix = get_index_for_model(sender)
    except KeyError:
        pass
    else:
        tasks.delete_indexed_document.delay(ix, instance.pk)


__all__ = (
    'sync_elasticsearch_on_model_update_or_create',
    'sync_elasticsearch_on_model_delete',
)
