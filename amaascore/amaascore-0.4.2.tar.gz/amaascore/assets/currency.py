from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.assets.asset import Asset


class Currency(Asset):

    def __init__(self, asset_id, deliverable, asset_status='Active', major=False, minor_unit_places=2, display_name='',
                 description='', country_id=None, *args, **kwargs):
        self.asset_class = 'Currency'
        self.deliverable = deliverable
        self.minor_unit_places = minor_unit_places
        self.major = major
        super(Currency, self).__init__(asset_manager_id=0, asset_id=asset_id, fungible=True, display_name=display_name,
                                       asset_class=self.asset_class, asset_status=asset_status, description=description,
                                       country_id=country_id, venue_id=None, currency=asset_id,
                                       *args, **kwargs)
                                    
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
