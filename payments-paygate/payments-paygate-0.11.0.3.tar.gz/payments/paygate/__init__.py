from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.translation import get_language

from .. import PaymentStatus
from ..core import BasicProvider
from .utils import calculate_md5, post_payment, validate_checksum

from math import trunc
from collections import OrderedDict
from datetime import datetime

class PaygateProvider(BasicProvider):

    def __init__(self, paygate_id=10011072130, **kwargs):
        self.paygate_id =  paygate_id # Test ID
        self.endpoint = 'https://secure.paygate.co.za/payweb3/process.trans'
        super(PaygateProvider, self).__init__(**kwargs)

    def get_action(self, payment):
        return self.endpoint

    def notify_response(self, request):
        if request.POST.get('AUTH_CODE'):
                    return HttpResponse('OK')

    def get_hidden_fields(self, payment):
        # Step 1 send transaction data to Paygate
        data = OrderedDict()
        response_data = OrderedDict()

        data['PAYGATE_ID'] = self.paygate_id
        data['REFERENCE'] = str(payment.id)
        data['AMOUNT'] = trunc(payment.total * 100)
        data['CURRENCY'] = 'ZAR'
        data['RETURN_URL'] = self.get_return_url(payment)
        data['TRANSACTION_DATE'] = payment.created.strftime('%Y-%m-%d %H:%M:%S')
        data['LOCALE'] = get_language()
        data['COUNTRY'] = 'ZAF'
        data['EMAIL'] = payment.billing_email
        data['NOTIFY_URL'] = payment.get_process_url()
        data['CHECKSUM'] = calculate_md5(data)
        data['url'] = 'https://secure.paygate.co.za/payweb3/initiate.trans'
        # Post data and validate response data
        hash_valid, response_data = post_payment(data)
        if not hash_valid: 
            return HttpResponseForbidden('FAILED')
        response_data.pop('PAYGATE_ID')
        response_data.pop('REFERENCE')
        return response_data


    def process_data(self, payment, request):
        success_url = payment.get_success_url()
        transaction_status = request.POST.get('TRANSACTION_STATUS')
        if payment.status == 'waiting':
            if transaction_status == '1':
                payment.captured_amount = payment.total
                payment.change_status(PaymentStatus.CONFIRMED)
                self.notify_response(request) # Reply with httpresponse OK 
                return redirect(success_url)
            elif transaction_status == '2':
                payment.change_status(PaymentStatus.REJECTED)
                self.notify_response(request)
                return redirect(payment.get_failure_url())
        return redirect(success_url)
