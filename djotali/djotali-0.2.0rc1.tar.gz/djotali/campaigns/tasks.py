# coding: utf-8
import celery
from billiard.exceptions import SoftTimeLimitExceeded
from celery import group
from celery.exceptions import Reject
from celery.result import GroupResult
from celery.utils.log import get_task_logger
from django.shortcuts import get_object_or_404

from djotali.campaigns.models import Campaign, Notification
from djotali.celery import app as celery_app
from djotali.core.services import ConsoleSmsSender
from djotali.contacts.templatetags.contacts_extras import format_number

logger = get_task_logger(__name__)
_sms_sender = ConsoleSmsSender(max_timeout=10)


class NotifyLogger:
    def __init__(self, campaign_id, campaign_name, phone_number):
        self.pattern = "CAMP_ID({}) - CAMP_NAME({}) - PHONE_NB({}) ".format(campaign_id, campaign_name, phone_number)

    def debug(self, message):
        logger.debug(self.pattern + message)

    def info(self, message):
        logger.info(self.pattern + message)

    def warning(self, message):
        logger.warning(self.pattern + message)

    def error(self, message):
        logger.error(self.pattern + message)


class NotificationException(Exception):
    pass


@celery_app.task(bind=True, max_retries=2, default_retry_delay=5)
def notify_campaign(self, campaign_id):
    try:
        _launch_campaign(campaign_id)
    except Campaign.DoesNotExist as e:
        logger.error("Unable to find Campaign %s" % campaign_id)
        raise Reject(e, requeue=False)
    except RuntimeError as e:
        logger.warning("Campaign {} failed because of {}".format(campaign_id, e))
        raise self.retry(exc=e, countdown=5)


class Notify(celery.Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error("Notification definitely failed for {}".format(args[1]))
        notification_id = args[0]
        Notification.tag_as_failed(notification_id)


@celery_app.task()
def notify_task(campaign_id, notification_id):
    _launch_campaign(campaign_id, notification_id)


@celery_app.task(base=Notify, bind=True, max_retries=2, soft_time_limit=5, throws=SoftTimeLimitExceeded)
def notify(self, notification_id, contact_phone_number, campaign_message, campaign_name, campaign_id):
    contact_phone_number = format_number(contact_phone_number)
    notify_logger = NotifyLogger(campaign_id, campaign_name, contact_phone_number)
    try:
        notify_logger.debug("Sending notification")
        sent = _sms_sender.send(contact_phone_number, campaign_message)
        if sent:
            Notification.tag_as_sent(notification_id)
            notify_logger.info("Notification succeeded !")
        else:
            notify_logger.error("An error occurs while sending message ! Retrying...")
            raise self.retry(countdown=60)
        return sent
    except Notification.DoesNotExist as e:
        notify_logger.error("Unable to find Notification %s" % notification_id)
        raise Reject(reason=e, requeue=False)
    except SoftTimeLimitExceeded as e:
        notify_logger.warning("Request timeout for notification - Retrying")
        raise self.retry(exc=e, countdown=5)
    except RuntimeError as e:
        raise self.retry(exc=e, countdown=2)


def _get_campaign_task_id(campaign_id):
    return 'send_sms_{}'.format(campaign_id)


def _launch_campaign(campaign_id, notification_id=None):
    if is_campaign_launched(campaign_id):
        return

    cpy_tenants_sms_result = _get_campaign_result(campaign_id)
    if cpy_tenants_sms_result is not None:
        cpy_tenants_sms_result.delete()

    campaign = get_object_or_404(Campaign, pk=campaign_id)
    if not campaign.is_started():
        logger.warning("Campaign %s (%s) not started !" % (campaign.name, campaign.id))
        raise Reject(None, requeue=False)

    notifications_query = Notification.objects
    if not notification_id:
        notifications_query = notifications_query.filter(campaign_id=campaign_id)
    else:
        notifications_query = notifications_query.filter(id=notification_id)

    notifications = notifications_query.exclude(status=1)

    if len(notifications) == 0:
        logger.info("No notification to send for campaign {} ({}) and notification id {}".format(campaign.name, campaign_id, notification_id))

    campaign_notification_tasks = \
        [notify.subtask(args=(notif.id, notif.contact.phone_number, campaign.message, campaign.name, campaign.id)) for notif in notifications]
    group(campaign_notification_tasks, task_id=_get_campaign_task_id(campaign_id))().save()


def is_campaign_launched(campaign_id):
    campaign_result = _get_campaign_result(campaign_id)
    return campaign_result is not None and not campaign_result.ready()


def _get_campaign_result(campaign_id):
    send_sms_cpy_group_id = _get_campaign_task_id(campaign_id)
    return GroupResult.restore(send_sms_cpy_group_id, app=celery_app)
