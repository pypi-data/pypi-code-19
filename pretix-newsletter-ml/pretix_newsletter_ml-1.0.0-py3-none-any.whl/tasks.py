import logging

from i18nfield.strings import LazyI18nString

from pretix.base.models import Event, Order
from pretix.base.services.mail import mail
from pretix.base.services.async import TransactionAwareTask
from pretix.celery_app import app

logger = logging.getLogger(__name__)


@app.task(base=TransactionAwareTask, bind=True, max_retries=10)
def newsletter_ml_order_placed(self, event: int, order: int) -> None:
    event = Event.objects.get(pk=event)
    order = Order.objects.get(pk=order)

    skip = (
        not event.settings.newsletter_ml_subscribe_address or (
            not event.settings.newsletter_ml_add_automatically
            and not order.meta_info_data.get('contact_form_data', {}).get('ml_newsletter') is True
        )
    )
    if skip:
        return

    mail(
        event.settings.newsletter_ml_subscribe_address,
        'subscribe',
        LazyI18nString('subscribe via pretix order {}'.format(order.code)),
        {},
        event,
        sender=order.email
    )

    order.log_action('pretix_newsletter_ml.subscribe', data={
        'email_address': order.email,
    })
