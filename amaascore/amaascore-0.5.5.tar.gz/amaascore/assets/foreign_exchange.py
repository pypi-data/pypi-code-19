from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.assets.asset import Asset


class ForeignExchangeBase(Asset):
    """ This class should never be instantiated """

    def __init__(self, asset_id, asset_status, description, major, country_codes, *args, **kwargs):
        self.asset_class = 'ForeignExchange'
        self.country_codes = country_codes
        self.major = major
        super(ForeignExchangeBase, self).__init__(asset_manager_id=0, asset_id=asset_id, fungible=True,
                                                  display_name=asset_id, roll_price=False,
                                                  asset_status=asset_status, description=description,
                                                  *args, **kwargs)

    def base_currency(self):
        return self.asset_id[0:3]

    def counter_currency(self):
        return self.asset_id[3:6]

    def get_country_codes(self):
        return self.country_codes
    
    def get_currencies(self):
        return [self.base_currency(), self.counter_currency()]
        
    @property
    def major(self):
        return self._major

    @major.setter
    def major(self, major):
        """

        :param major:
        :return:
        """
        if major:
            self._major = major
        else:
            self._major = False

    @property
    def country_codes(self):
        return self._country_codes

    @country_codes.setter
    def country_codes(self, country_codes):
        """

        :param country_codes:
        :return:
        """
        self._country_codes = country_codes

class ForeignExchange(ForeignExchangeBase):
    """
    Currently modelling spot and forward as the same, just two different dates on the transaction.  We might need to
    change that.
    """
    def __init__(self, asset_id, asset_status='Active', country_codes=[], major=False, description='', *args, **kwargs):
        super(ForeignExchange, self).__init__(asset_id=asset_id, asset_status=asset_status, description=description,
                                              country_codes=country_codes, major=major,
                                              *args, **kwargs)


class NonDeliverableForward(ForeignExchangeBase):
    """
    Currently modelling spot and forward as the same, just two different dates on the transaction.  We might need to
    change that.
    """

    def __init__(self, asset_id, asset_status='Active', description='', major=False, country_codes=[], *args, **kwargs):
        super(NonDeliverableForward, self).__init__(asset_id=asset_id, asset_status=asset_status, country_codes=country_codes,
                                                    major=major, description=description, *args, **kwargs)

