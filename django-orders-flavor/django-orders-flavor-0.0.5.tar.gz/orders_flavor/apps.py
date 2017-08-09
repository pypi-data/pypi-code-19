from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OrdersAppConfig(AppConfig):
    name = 'orders_flavor'
    verbose_name = _('Orders')

    def ready(self):
        import orders_flavor.signals.orders  # NOQA
        import orders_flavor.signals.paypal  # NOQA
