# coding: utf-8
import logging

import celery
from celery.bin.base import Error

"""
Fonctions utilitaires
"""


def get_logger(name):
    return logging.getLogger(name)


def is_celery_running():
    try:
        celery_ping_response = celery.current_app.control.inspect().ping()
        if not celery_ping_response:
            return False
        for response in celery_ping_response.values():
            if 'ok' not in response:
                return False
    except Error:
        return False
    return True
