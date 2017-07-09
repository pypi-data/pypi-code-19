import urllib
import logging

from django.conf.settings import (
    DRAGONPAY_ID, DRAGONPAY_MERCHANT_SECRET, DRAGONPAY_MERCHANT_URL,
    DRAGONPAY_PAY_URL)
from django_dragonpay.utils import get_dragonpay_digest

logger = logging.getLogger('dragonpay.http_get')


def get_txn_url(txn_id, amount, description, email, *params):
    digest_list = [DRAGONPAY_ID, txn_id, amount, description, email]

    payload = {
        'merchantid': DRAGONPAY_ID,
        'txnid': txn_id,
        'amount ': amount,
        'ccy ': 'PHP',
        'description': description,
        'email': email,
        'digest': get_dragonpay_digest(digest_list)
    }

    if len(params) > 2:
        raise Exception(
            'You can only have a maximum of 2 DragonPay request params.')

    # include any params that were included
    for i, param in enumerate(params):
        payload['param%s' % (i + 1)] = param

    return DRAGONPAY_PAY_URL + urllib.urlencode(payload)


def get_txn_status(txn_id):
    payload = {
        'merchantid': DRAGONPAY_ID,
        'merchantpwd': DRAGONPAY_MERCHANT_SECRET,
        'txnid': txn_id,
        'op': 'GETSTATUS'
    }

    response.POST(DRAGONPAY_MERCHANT_URL, data=payload)


def cancel_transaction(txn_id):
    payload = {
        'merchantid': DRAGONPAY_ID,
        'merchantpwd': DRAGONPAY_MERCHANT_SECRET,
        'txnid': txn_id, 'op': 'VOID'
    }

    response.POST(DRAGONPAY_MERCHANT_URL, data=payload)

