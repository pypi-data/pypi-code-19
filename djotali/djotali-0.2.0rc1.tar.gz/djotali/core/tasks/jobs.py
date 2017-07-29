# coding: utf-8

from celery.utils.log import get_task_logger

from djotali.celery import app as celery_app

logger = get_task_logger(__name__)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, say_hi.s(), name='Say hi every 10 seconds to someone')

    # sender.add_periodic_task(crontab(minute=1), say_hi.s())


@celery_app.task
def say_hi():
    from faker import Faker
    fake = Faker('en_US')
    print("Hello %s %s" % (fake.first_name, fake.last_name))
