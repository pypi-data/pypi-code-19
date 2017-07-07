# -*- coding: utf-8 -*-
from __future__ import absolute_import
import string
from django.core import cache

from .models import Term


def index_list(reset=False):
    """Restituisce l'elenco delle lettere e il relativo stato (active per le lettere che hanno voci sottostanti)"""
    cache_key = '{}:index_list'.format(__name__)
    index = None if reset else cache.cache.get(cache_key)

    if index is None:
        attive = {t.pk[0] for t in Term.objects.all()}
        index = [{'val': iniziale, 'active': iniziale.lower() in attive} for iniziale in string.uppercase]
        cache.cache.set(cache_key, index)

    return index

