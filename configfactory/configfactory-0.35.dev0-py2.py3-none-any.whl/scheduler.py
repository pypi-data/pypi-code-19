import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

logger = logging.getLogger(__name__)

SCHEDULER_SETTINGS = getattr(settings, 'SCHEDULER_SETTINGS', {})


def run():
    """Run scheduler."""

    from configfactory import backup

    logger.info('Starting scheduler')

    # Initialize scheduler
    scheduler = BackgroundScheduler(SCHEDULER_SETTINGS)

    # Add jobs
    scheduler.add_job(backup.dump,
                      trigger='interval',
                      seconds=backup.BACKUP_INTERVAL)

    scheduler.add_job(backup.cleanup,
                      trigger='interval',
                      seconds=backup.BACKUP_INTERVAL)

    # Start scheduler
    scheduler.start()
    try:
        while True:
            time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
