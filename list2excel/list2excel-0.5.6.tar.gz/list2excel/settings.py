# -*- coding: utf-8 -*-
from django.conf import settings

MAX_FILENAME_LENGTH = 64
MAX_ONLINE_EXPORT_RECORDS = getattr(
    settings, 'LIST2EXCEL_MAX_EXPORT_RECORDS', 5000)
GLOBAL_ACTIONS = getattr(settings, 'LIST2EXCEL_GLOBAL_ACTIONS', True)