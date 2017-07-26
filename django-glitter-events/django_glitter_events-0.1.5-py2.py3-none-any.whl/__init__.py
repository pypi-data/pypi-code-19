# -*- coding: utf-8 -*-
from django.conf import settings

default_app_config = 'glitter_events.apps.GlitterEventsConfig'

USE_LOCATIONS = False
if hasattr(settings, 'GLITTER_EVENTS_USE_LOCATIONS'):
    USE_LOCATIONS = settings.GLITTER_EVENTS_USE_LOCATIONS 
