# coding: utf-8
import hues
from tqdm import tqdm

from django.core.management.base import BaseCommand

from elasticsearch_flex.indexes import registered_indices


class Command(BaseCommand):
    help = 'Setup Search Index'

    def handle(self, *args, **options):
        indices = registered_indices()
        if len(indices):
            hues.info('Discovered', len(indices), 'Indexes')
        else:
            hues.warn('No search indexes found')
        for i, index in enumerate(indices, 1):
            hues.info('==> Indexing objects from', index.model, 'in', index)
            for obj in tqdm(index.queryset):
                doc = index.init_using_pk(obj.pk)
                doc.prepare()
                doc.save()
            hues.success('--> {0}/{1} indexed.'.format(i, len(indices)))
