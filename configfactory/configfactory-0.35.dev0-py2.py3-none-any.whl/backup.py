import logging
import os

import appdirs
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from configfactory.support import config
from configfactory.utils import current_timestamp

BACKUP_DIR = config.get(
    'backup.dir',
    default=appdirs.user_data_dir('configfactory_backup')
)

BACKUP_INTERVAL = config.get('backup.interval', default=3600)  # seconds

BACKUP_COUNT = config.get('backup.count', default=20)

logger = logging.getLogger(__name__)


def get_file(filename):
    return os.path.join(BACKUP_DIR, filename)


def dump():

    logger.info("Running settings backup...")

    name = 'backup_{}.json'.format(current_timestamp())
    call_command('dumpdata', 'configfactory.Component', format='json',
                 output=get_file(name))
    return name


def cleanup():

    logger.info("Running settings backup cleanup...")

    dt_now = timezone.now()
    check_datetime = timezone.make_aware(
        dt_now - timezone.timedelta(seconds=BACKUP_INTERVAL))
    backups = [
        b['name']
        for b in get_all()[BACKUP_COUNT:]
        if check_datetime > b['created_at']
    ]
    for filename in backups:
        delete(filename)


def load(filename):
    call_command('loaddata', get_file(filename))


def exists(filename):
    return os.path.exists(get_file(filename))


def delete(filename):
    if exists(filename):
        os.remove(get_file(filename))


def get_all():
    return [
        {
            'name': filename,
            'url': reverse('serve_backup_file', kwargs={
                'filename': filename
            }),
            'size': os.path.getsize(get_file(filename)),
            'created_at': timezone.datetime.fromtimestamp(
                os.path.getctime(get_file(filename)),
                tz=timezone.get_current_timezone()
            )
        } for filename in sorted(os.listdir(BACKUP_DIR), reverse=True)
        if os.path.isfile(get_file(filename))
        and filename.endswith('.json')
    ]
