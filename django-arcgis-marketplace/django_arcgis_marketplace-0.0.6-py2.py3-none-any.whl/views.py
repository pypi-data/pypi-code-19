import urllib.parse
import uuid

from django.conf import settings
from django.urls import reverse
from django.views.generic import DetailView

from paypal.standard.forms import PayPalPaymentsForm

from . import models


class ItemPaypalFormView(DetailView):
    model = models.Item
    template_name = 'arcgis_marketplace/paypal_form.html'

    def get_host_url(self, path):
        host = self.request.META.get('HTTP_HOST', '')
        return urllib.parse.urljoin(host, path)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PayPalPaymentsForm(initial={
            'business': settings.PAYPAL_BUSINESS,
            'amount': "{:.2f}".format(self.object.price),
            'item_name': self.object.title,
            'invoice': uuid.uuid4().hex,
            'notify_url': self.get_host_url(reverse('paypal-ipn')),
            'return_url': self.get_host_url('paypal-success'),
            'cancel_return': self.get_host_url('paypal-cancel'),
            'currency_code': 'EUR'
        })

        return context
