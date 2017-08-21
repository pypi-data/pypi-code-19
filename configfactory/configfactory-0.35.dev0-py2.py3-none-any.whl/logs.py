import os

import appdirs
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

LOGGING_DIR = getattr(
    settings,
    'LOGGING_DIR',
    appdirs.user_data_dir('logs')
)

LOGGING_FILENAME = getattr(
    settings,
    'LOGGING_FILENAME',
    'configfactory.log'
)


def get_file(filename):
    return os.path.join(
        LOGGING_DIR,
        filename
    )


def exists(filename):
    return os.path.exists(get_file(filename))


def get_all():
    return [
        {
            'name': filename,
            'url': reverse('serve_log_file', kwargs={
                'filename': filename
            }),
            'size': os.path.getsize(get_file(filename)),
            'created_at': timezone.datetime.fromtimestamp(
                os.path.getctime(get_file(filename)),
                tz=timezone.get_current_timezone()
            )
        } for filename in sorted(os.listdir(LOGGING_DIR), reverse=True)
        if os.path.isfile(get_file(filename)) and LOGGING_FILENAME in filename
    ]
