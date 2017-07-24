from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal

from amaascore.core.amaas_model import AMaaSModel


class Charge(AMaaSModel):

    def __init__(self, charge_value, currency, net_affecting=True, version=1, *args, **kwargs):
        self.charge_value = charge_value
        self.currency = currency
        self.net_affecting = net_affecting
        self.version = version
        super(Charge, self).__init__(*args, **kwargs)

    @property
    def charge_value(self):
        return self._charge_value

    @charge_value.setter
    def charge_value(self, value):
        """
        Force the charge_value to always be a decimal
        :param value:
        :return:
        """
        self._charge_value = Decimal(value)


class Code(AMaaSModel):

    def __init__(self, code_value, version=1, *args, **kwargs):
        self.code_value = code_value
        self.version = version
        super(Code, self).__init__(*args, **kwargs)


class Comment(AMaaSModel):

    def __init__(self, comment_value, version=1, *args, **kwargs):
        self.comment_value = comment_value
        self.version = version
        super(Comment, self).__init__(*args, **kwargs)


class Link(AMaaSModel):

    def __init__(self, linked_transaction_id, version=1, *args, **kwargs):
        self.linked_transaction_id = linked_transaction_id
        self.version = version
        super(Link, self).__init__(*args, **kwargs)


class Party(AMaaSModel):

    def __init__(self, party_id, version=1, *args, **kwargs):
        self.party_id = party_id
        self.version = version
        super(Party, self).__init__(*args, **kwargs)


class Rate(AMaaSModel):
    
    def __init__(self, rate_value, version=1, *args, **kwargs):
        self.rate_value = rate_value
        self.version = version
        super(Rate, self).__init__(*args, **kwargs)

    @property
    def rate_value(self):
        return self._rate_value

    @rate_value.setter
    def rate_value(self, value):
        """
        Force the charge_value to always be a decimal
        :param value:
        :return:
        """
        self._rate_value = Decimal(value)


class Reference(AMaaSModel):
    
    def __init__(self, reference_value, *args, **kwargs):
        self.reference_value = reference_value
        super(Reference, self).__init__(*args, **kwargs)

