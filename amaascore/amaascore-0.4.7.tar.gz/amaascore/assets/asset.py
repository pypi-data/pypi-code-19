from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date
from dateutil.parser import parse
import re
import sys
import uuid

from amaascore.assets.children import Link
from amaascore.core.amaas_model import AMaaSModel
from amaascore.core.comment import Comment
from amaascore.core.reference import Reference

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class Asset(AMaaSModel):

    @staticmethod
    def children():
        return {'comments': Comment, 'links': Link, 'references': Reference}

    def __init__(self, asset_manager_id, fungible, asset_issuer_id=None, asset_id=None, asset_status='Active',
                 country_id=None, venue_id=None, currency=None, issue_date=date.min,
                 roll_price=True, display_name='', description='',
                 comments=None, links=None, references=None, client_additional=None,
                 *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        self.asset_id = asset_id or uuid.uuid4().hex
        if not hasattr(self, 'asset_class'):  # A more specific child class may have already set this
            self.asset_class = 'Asset'
        # This can be overridden if necessary but I think it probably shouldn't
        self.asset_type_display = ' '.join(re.findall('[A-Z][^A-Z]*', self.__class__.__name__))
        self.asset_type = self.__class__.__name__
        self.fungible = fungible
        self.asset_issuer_id = asset_issuer_id
        self.asset_status = asset_status
        self.country_id = country_id
        self.venue_id = venue_id
        self.currency = currency
        self.issue_date = issue_date
        self.roll_price = roll_price
        self.display_name = display_name
        self.description = description
        self.client_additional = client_additional  # A field to allow people to build their own assets
        # Defaults are here not in constructor for mutability reasons.
        self.comments = comments.copy() if comments else {}
        self.links = links.copy() if links else {}
        self.references = references.copy() if references else {}
        self.references['AMaaS'] = Reference(reference_value=self.asset_id)  # Upserts the AMaaS Reference
        super(Asset, self).__init__(*args, **kwargs)

    def reference_types(self):
        """
        TODO - are these helper functions useful?
        :return:
        """
        return self.references.keys()

    @property
    def issue_date(self):
        if hasattr(self, '_issue_date'):
            return self._issue_date

    @issue_date.setter
    def issue_date(self, value):
        """
        The date on which the asset is issued
        :param value:
        :return:
        """
        if value:
            self._issue_date = parse(value).date() if isinstance(value, type_check) else value

    @property
    def maturity_date(self):
        if hasattr(self, '_maturity_date'):
            return self._maturity_date

    @maturity_date.setter
    def maturity_date(self, value):
        """
        The date on which the asset matures and no longer holds value
        :param value:
        :return:
        """
        if value:
            self._maturity_date = parse(value).date() if isinstance(value, type_check) else value

    def __str__(self):
        return "Asset object - ID: %s" % self.asset_id

    def get_country_codes(self):
        return [self.country_id]

    def country_and_venue_codes(self):
        """
        This function returns dictionary in the format of {"country_codes": [XYZ, ABC], "venue_id": [ABC]} 
        Where country_codes = self.country_id and venue_id = self.venue_id
        except for FX where we also return the country_ids associated with the legs of the FX transaction 
        (e.g. USDJPY returns USA + JPN).
        """
        codes = {'country_codes': self.get_country_codes(), 'venue_id': [self.venue_id]}
        return codes
        
    def get_currencies(self):
        return [self.currency]

