from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from amaascore.asset_managers.utils import json_to_asset_manager, json_to_relationship, json_to_eod_book
from amaascore.config import ENVIRONMENT
from amaascore.core.interface import Interface


class AssetManagersInterface(Interface):
    """
    The interface to the Asset Managers service for reading Asset Manager information.
    """

    def __init__(self, environment=ENVIRONMENT, logger=None, endpoint=None, username=None, password=None):
        self.logger = logger or logging.getLogger(__name__)
        super(AssetManagersInterface, self).__init__(endpoint=endpoint, endpoint_type='asset_managers',
                                                     environment=environment, username=username, password=password)

    def new(self, asset_manager):
        self.logger.info('New Asset Manager: %s', asset_manager.asset_manager_id)
        url = '%s/asset-managers' % self.endpoint
        response = self.session.post(url, json=asset_manager.to_interface())
        if response.ok:
            asset_manager = json_to_asset_manager(response.json())
            self.logger.info('Successfully Created Asset Manager: %s', asset_manager.asset_manager_id)
            return asset_manager
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve(self, asset_manager_id):
        self.logger.info('Retrieve Asset Manager: %s', asset_manager_id)
        url = '%s/asset-managers/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url)
        if response.ok:
            self.logger.info('Successfully Retrieved Asset Manager: %s', asset_manager_id)
            return json_to_asset_manager(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def deactivate(self, asset_manager_id):
        """
        Is is only possible to deactivate an asset manager if your client_id is also the client_id that was used
        to originally create the asset manager.

        :param asset_manager_id:
        :return:
        """
        self.logger.info('Deactivate Asset Manager: %s', asset_manager_id)
        url = '%s/asset-managers/%s' % (self.endpoint, asset_manager_id)
        response = self.session.delete(url)
        if response.ok:
            self.logger.info('Successfully deactivated Asset Manager: %s', asset_manager_id)
            return json_to_asset_manager(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def search(self, asset_manager_ids=None, client_ids=None):
        self.logger.info('Search for Asset Managers: %s', asset_manager_ids)
        search_params = {}
        # Potentially roll this into a loop through args rather than explicitly named - depends on additional validation
        if asset_manager_ids:
            search_params['asset_manager_ids'] = ','.join([str(amid) for amid in asset_manager_ids])
        if client_ids:
            search_params['client_ids'] = ','.join(client_ids)
        url = self.endpoint + '/asset-managers'
        response = self.session.get(url, params=search_params)
        if response.ok:
            asset_managers = [json_to_asset_manager(json_asset_manager) for json_asset_manager in response.json()]
            self.logger.info('Returned %s Asset Managers.', len(asset_managers))
            return asset_managers
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def new_relationship(self, relationship):
        self.logger.info('New Asset Manager Relationship: %s and %s', relationship.asset_manager_id,
                         relationship.related_id)
        url = '%s/asset-manager-relationships/%s' % (self.endpoint, relationship.asset_manager_id)
        response = self.session.post(url, json=relationship.to_interface())
        if response.ok:
            self.logger.info('Successfully Created Asset Manager Relationship: %s', relationship.asset_manager_id)
            return json_to_relationship(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def amend_relationship(self, relationship):
        self.logger.info('Amend Asset Manager Relationship: %s and %s', relationship.asset_manager_id,
                         relationship.related_id)
        url = '%s/asset-manager-relationships/%s' % (self.endpoint, relationship.asset_manager_id)
        response = self.session.put(url, json=relationship.to_interface())
        if response.ok:
            self.logger.info('Successfully Amended Asset Manager Relationship: %s', relationship.asset_manager_id)
            return json_to_relationship(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve_relationships(self, asset_manager_id, related_id=None, include_inactive=False):
        self.logger.info('Retrieve Asset Manager Relationship: %s', asset_manager_id)
        url = '%s/asset-manager-relationships/%s' % (self.endpoint, asset_manager_id)
        params = {'include_inactive': include_inactive}
        if related_id:
            params['related_id'] = related_id
        response = self.session.get(url, params=params)
        if response.ok:
            self.logger.info('Successfully Amended Asset Manager Relationship: %s', asset_manager_id)
            return [json_to_relationship(json_relationship) for json_relationship in response.json()]
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve_eod_books(self, asset_manager_id=None, book_id=None):
        self.logger.info('Search for EOD Books. asset_manager_id: %s, book_id: %s', asset_manager_id, book_id)
        search_params = {}
        # Potentially roll this into a loop through args rather than explicitly named - depends on additional validation
        if asset_manager_id:
            search_params['asset_manager_id'] = asset_manager_id
        if book_id:
            search_params['book_id'] = book_id
        url = self.endpoint + '/eod-books'
        response = self.session.get(url, params=search_params)
        if response.ok:
            eod_books = [json_to_eod_book(json_eod_book) for json_eod_book in response.json()]
            self.logger.info('Returned %s EOD Books.', len(eod_books))
            return eod_books
        else:
            self.logger.error(response.text)
            response.raise_for_status()