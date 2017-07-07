# -*- coding: utf-8 -*-
from django.conf import settings

TERMS_INDEX_COLUMNS = getattr(settings, 'GLOSSARY_TERMS_INDEX_COLUMNS', 1)
