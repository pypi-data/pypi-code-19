# -*- coding: utf-8 -*-
##
## This file is part of the SixPay Indico EPayment Plugin.
## Copyright (C) 2017 Max Fischer
##
## This is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
## License, or (at your option) any later version.
##
## This software is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Indico;if not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import, division
import urlparse
import requests
from xml.dom.minidom import parseString

from MaKaC.epayment import BaseEPayMod, BaseTransaction
from MaKaC.common.timezoneUtils import nowutc


from .webinterface import urlHandlers as localUrlHandlers
from . import MODULE_ID


class TransactionError(BaseException):
    """An error occurred inside the transaction to SixPay"""


class SixPayFormatFieldMap(object):
    """
    Mapping lazily providing format fields

    :type registrant: MaKaC.registration.Registrant
    :type conference: MaKaC.conference.Conference
    """
    def __init__(self, registrant, conference):
        self.registrant = registrant
        self.conference = conference
        self._field_cache = {}
        self._field_maker = {
            'user_id': registrant.getId, 'user_name': lambda: registrant.getFullName(title=False, firstNameFirst=True),
            'user_firstname': registrant.getFirstName, 'user_lastname': registrant.getSurName,
            'event_id': conference.getId, 'event_title': conference.getTitle,
            'eventuser_id': registrant.getIdPay,
        }

    def __getitem__(self, key):
        try:
            item = self._field_cache[key]
        except KeyError:
            item = self._field_cache[key] = self._field_maker[key]()
        return item

    def __setitem__(self, key, value):
        self._field_cache[key] = value

    def __repr__(self):
        return '%s(registrant=%s, conference=%s)' % (self.__class__.__name__, self.registrant, self.conference)


class SixPayMod(BaseEPayMod):
    """
    Payment Module for SIX Payment Service

    :param data: mapping to initialise fields
    :type data: dict or None
    """
    #: default settings used when setting fields via `data`
    default_settings = {
        'title': "Six Payment Services",
        'url': "https://www.saferpay.com/hosting",
        'account_id': "",
        'notification_mail': "",
        'user_description': "%(event_title)s, %(user_name)s",
        'order_identifier': "%(eventuser_id)s",
    }

    def __init__(self, data=None):
        BaseEPayMod.__init__(self)
        #: title of this payment method
        self._title = self.default_settings['title']
        #: URL for the saferpay https interface
        self._url = self.default_settings['url']
        #: saferpay account ID of the conference
        self.account_id = self.default_settings['account_id']
        #: description for transaction presented to registrant
        self.user_description = self.default_settings['user_description']
        #: internal description for transaction for organiser and accounting
        self.order_identifier = self.default_settings['order_identifier']
        #: mail to send confirmations to
        self.notification_mail = self.default_settings['notification_mail']
        if data is not None:
            self.setValues(data)

    def getId(self):
        return MODULE_ID

    def clone(self, newSessions):
        """Return a clone of this instance"""
        self_clone = SixPayMod()
        self_clone.setValues(self.getValues())
        self_clone.setEnabled(self.isEnabled())
        return self_clone

    def setValues(self, data):
        """
        Set all fields from mapping

        :param data: mapping to initialise fields
        :type data: dict or None

        :note: any field missing in `data` will be set to its default value
        """
        for key in self.default_settings:
            value = data.get(key) or self.default_settings[key]
            setattr(self, key, value)

    def getValues(self):
        """
        Get all fields as a mapping

        :return: mapping of all fields
        :rtype: dict

        :note: any field missing will be set to its default value
        """
        return {
            key: getattr(self, key, self.default_settings[key]) for key in self.default_settings
        }

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        # ensure a trailing slash at end of path, or merging endpoints does not work
        url = urlparse.urlparse(value)
        url = url._replace(path=url.path.rstrip('/') + '/')
        self._url = url.geturl()

    @staticmethod
    def _perform_request(endpoint, **params):
        """Perform a POST request"""
        url_request = requests.post(endpoint, **params)
        # raise any request errors
        url_request.raise_for_status()
        # raise errors in response
        if url_request.text.startswith('ERROR'):
            raise TransactionError('Failed request to SixPay service: %s' % url_request.text)
        return url_request

    def getFormHTML(self, prix, Currency, conf, registrant, lang="en_GB", secure=False):
        """Generates the action of the button presented to the user for payment"""
        payment_url = self._get_payment_url(prix, Currency, conf, registrant, lang, secure)
        payment_action = """<form action="%s" method="POST" id="%s"/>""" % (payment_url, self.getId())
        return payment_action

    def _get_user_description(self, format_map):
        user_description = self.user_description
        user_description %= format_map
        return user_description

    def _get_order_identifier(self, format_map):
        order_identifier = self.order_identifier
        order_identifier %= format_map
        return ''.join(order_identifier.split())

    def _get_payment_url(self, prix, Currency, conf, registrant, lang, secure):
        """
        Generate Payment URL for User

        This method uses the payment details to generate a signed payment URL
        that is secure against manipulation.
        Transmitting the payment request to Six is separate from prompting the
        user to avoid modification of payment details.

        :type registrant: MaKaC.registration.Registrant
        :type conf: MaKaC.conference.Conference
        """
        endpoint = urlparse.urljoin(self.url, 'CreatePayInit.asp')
        # keys for formatting strings
        format_map = SixPayFormatFieldMap(registrant=registrant, conference=conf)
        # description of transaction presented to user
        user_description = self._get_user_description(format_map)
        # internal description of transaction for organiser and accounting
        order_identifier = self._get_order_identifier(format_map)
        # parameters for callbacks so that indico can identify the transaction subject
        callback_params = {'target': conf, 'registrantId': registrant.getId()}
        parameters = {
            'ACCOUNTID': str(self.account_id),
            # indico handles price as largest currency, but six expects smallest
            # e.g. EUR: indico uses 100.2 Euro, but six expects 10020 Cent
            'AMOUNT': '%d' % (prix*100),
            'CURRENCY': Currency,
            'DESCRIPTION': user_description[:50],
            'ORDERID': order_identifier[:80],
            'SHOWLANGUAGES': 'yes',
            # callbacks for the service to redirect users back to indico
            'SUCCESSLINK': localUrlHandlers.UHPayTransactionSuccess.getURL(**callback_params),
            'FAILLINK': localUrlHandlers.UHPayTransactionFaillink.getURL(**callback_params),
            'BACKLINK': localUrlHandlers.UHPayTransactionBacklink.getURL(**callback_params),
            # callback for the service to confirm transaction
            'NOTIFYURL': localUrlHandlers.UHPayTransactionNotifyUrl.getURL(**callback_params),
        }
        if self.notification_mail:
            parameters['NOTIFYADDRESS'] = self.notification_mail
        url_request = self._perform_request(endpoint, data=parameters)
        return str(url_request.text)

    def verify_transaction(self, data, signature, registrant):
        """Ensure the transaction is correct in Indico and SixPay"""
        # DATA: '<IDP
        #           MSGTYPE="PayConfirm" TOKEN="(unused)" VTVERIFY="(obsolete)" KEYID="1-0"
        #           ID="9SUO5zbOGY6OUA45b222bhvrpW2A"
        #           ACCOUNTID="401860-17795278"
        #           PROVIDERID="90"
        #           PROVIDERNAME="Saferpay Test Card"
        #           PAYMENTMETHOD="6"
        #           ORDERID="c281r4"
        #           AMOUNT="100"
        #           CURRENCY="EUR"
        #           IP="141.3.200.120"
        #           IPCOUNTRY="DE"
        #           CCCOUNTRY="US"
        #           MPI_LIABILITYSHIFT="yes"
        #           MPI_TX_CAVV="jAABBIIFmAAAAAAAAAAAAAAAAAA="
        #           MPI_XID="VVE3DQlhXR8PBD5JPzYGWW5FNgI="
        #           ECI="1"
        #           CAVV="jAABBIIFmAAAAAAAAAAAAAAAAAA="
        #           XID="VVE3DQlhXR8PBD5JPzYGWW5FNgI=" />'
        mdom = parseString(data)
        attributes = mdom.documentElement.attributes
        idp_data = {
            attributes.item(idx).name: attributes.item(idx).value
            for idx in range(attributes.length)
        }
        if self._verify_confirmation(data, signature, idp_data=idp_data):
            conference = registrant.getConference()
            format_map = SixPayFormatFieldMap(registrant=registrant, conference=conference)
            transaction = TransactionSixPay(
                user_id=registrant.getId(), event_id=conference.getId(),
                signature=signature, amount=(int(idp_data['AMOUNT']) / 100.0), currency=idp_data['CURRENCY'],
                six_id=idp_data['ID'], order_id=idp_data['ORDERID'], subject=self._get_user_description(format_map)
            )
            # verification may be triggered multiple times
            if registrant.getPayed() and registrant.getTransactionInfo() == transaction:
                return True
            self._complete_transaction(idp_data=idp_data)
            registrant.setTransactionInfo(transaction)
            registrant.setPayed(True)
            registration_form = registrant.getConference().getRegistrationForm()
            registration_form.getNotification().sendEmailNewRegistrantConfirmPay(
                registration_form, registrant
            )
        return False

    def _verify_confirmation(self, data, signature, idp_data):
        """ask for confirmation from SixPay for the signature of the transaction"""
        endpoint = urlparse.urljoin(self.url, 'VerifyPayConfirm.asp')
        url_request = self._perform_request(endpoint, data={'DATA': data, 'SIGNATURE': signature})
        if url_request.text.startswith('OK:'):
            # text = 'OK:ID=56a77rg243asfhmkq3r&TOKEN=%3e235462FA23C4FE4AF65'
            confirmation = dict(key_value.split('=') for key_value in url_request.text.split(':', 1)[1].split('&'))
            if idp_data['ID'] != confirmation['ID'] or idp_data['ID'] != confirmation['ID']:
                raise TransactionError('Mismatched verification and confirmation data')
            return True
        raise RuntimeError("Expected reply 'OK:ID=...&TOKEN=...', got %r" % url_request.text)

    def _complete_transaction(self, idp_data):
        """inform SixPay that we agree to the transaction"""
        endpoint = urlparse.urljoin(self.url, 'PayCompleteV2.asp')
        data = {'ACCOUNTID': idp_data['ACCOUNTID'], 'ID': idp_data['ID']}
        if 'test.' in self.url:
            data['spPassword'] = '8e7Yn5yk'
        url_request = self._perform_request(endpoint, data=data)
        return url_request.text.startswith('OK')

    def getConfModifEPaymentURL(self, conf):
        """URL for applying settings for the EPayment of a single event/conference"""
        return localUrlHandlers.UHConfModifEPaymentSixPay.getURL(conf)


class TransactionSixPay(BaseTransaction):
    """Completed Transaction for SIX Payment Service"""
    def __init__(self, user_id, event_id, signature, amount, currency, six_id, order_id, date=None, subject=None):
        BaseTransaction.__init__(self)
        self.user_id = user_id
        self.event_id = event_id
        self.signature = signature
        self.amount = amount
        self.currency = currency
        self.six_id = six_id
        self.order_id = order_id
        self.date = date or nowutc()
        self.subject = subject or ('Event %s, Registrant %s' % (self.event_id, self.user_id))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.six_id == other.six_id and self.order_id == other.order_id and self.signature == other.signature
        else:
            return NotImplemented

    def getId(self):
        try:
            return self._id
        except AttributeError:
            self._id = "sixpay"
            return self._id

    def _form_data(self):
        return (
                ('Service', 'SixPay'),
                ('Date', self.date),
                ('Amount', '%.2f %s' % (self.amount, self.currency)),
                ('Description', self.subject),
                ('Identifier', self.order_id),
                ('Transaction ID', self.six_id),
            )

    def getTransactionHTML(self):
        """HTML for displaying transaction in Indico"""
        entry = """\
                          <tr>
                            <td align="right"><b>%s</b></td>
                            <td align="left">%s</td>
                          </tr>"""
        return """\
                        <table>
%s
                        </table>""" % '\n'.join(
            entry % (name, value)
            for name, value in
            self._form_data()
        )

    def getTransactionTxt(self):
        """Text for displaying transaction in mails"""
        entry = """%-16s %s"""
        return '\n'.join(
            entry % (name, value)
            for name, value in
            self._form_data()
        )


def getPayMod():
    return SixPayMod()


def getPayModClass():
    return SixPayMod
