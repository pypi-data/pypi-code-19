from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import json

from amaascore.config import ENVIRONMENT
from amaascore.core.amaas_model import json_handler
from amaascore.core.interface import Interface
from amaascore.transactions.utils import json_to_transaction, json_to_position


class TransactionsInterface(Interface):

    def __init__(self, environment=ENVIRONMENT, logger=None, endpoint=None, username=None, password=None):
        self.logger = logger or logging.getLogger(__name__)
        super(TransactionsInterface, self).__init__(endpoint=endpoint, endpoint_type='transactions',
                                                    environment=environment, username=None, password=None)

    def new(self, transaction):
        self.logger.info('New Transaction - Asset Manager: %s - Transaction ID: %s', transaction.asset_manager_id,
                         transaction.transaction_id)
        url = '%s/transactions/%s' % (self.endpoint, transaction.asset_manager_id)
        response = self.session.post(url, json=transaction.to_interface())
        if response.ok:
            transaction = json_to_transaction(response.json())
            return transaction
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def amend(self, transaction):
        self.logger.info('Amend Transaction - Asset Manager: %s - Transaction ID: %s', transaction.asset_manager_id,
                         transaction.transaction_id)
        url = '%s/transactions/%s/%s' % (self.endpoint, transaction.asset_manager_id, transaction.transaction_id)
        response = self.session.put(url, json=transaction.to_interface())
        if response.ok:
            transaction = json_to_transaction(response.json())
            return transaction
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def partial(self, asset_manager_id, transaction_id, updates):
        self.logger.info('Partial Amend Transaction - Asset Manager: %s - Transaction ID: %s', asset_manager_id,
                         transaction_id)
        url = '%s/transactions/%s/%s' % (self.endpoint, asset_manager_id, transaction_id)
        response = self.session.patch(url, data=json.dumps(updates, default=json_handler), headers=self.json_header)
        if response.ok:
            transaction = json_to_transaction(response.json())
            return transaction
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve(self, asset_manager_id, transaction_id, version=None):
        self.logger.info('Retrieve Transaction - Asset Manager: %s - Transaction ID: %s', asset_manager_id,
                         transaction_id)
        url = '%s/transactions/%s/%s' % (self.endpoint, asset_manager_id, transaction_id)
        if version:
            url += '?version=%d' % int(version)
        response = self.session.get(url)
        if response.ok:
            return json_to_transaction(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def transactions_by_asset_manager(self, asset_manager_id):
        self.logger.info('Retrieve Transactions by Asset Manager: %s', asset_manager_id)
        url = '%s/transactions/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url)
        if response.ok:
            transactions = [json_to_transaction(json_transaction) for json_transaction in response.json()]
            self.logger.info('Returned %s Transactions.', len(transactions))
            return transactions
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def cancel(self, asset_manager_id, transaction_id):
        self.logger.info('Cancel Transaction - Asset Manager: %s - Transaction ID: %s', asset_manager_id,
                         transaction_id)
        url = '%s/transactions/%s/%s' % (self.endpoint, asset_manager_id, transaction_id)
        response = self.session.delete(url)
        if response.ok:
            self.logger.info('Successfully Cancelled - Asset Manager: %s - Transaction ID: %s.', asset_manager_id,
                             transaction_id)
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def search(self, asset_manager_ids=[], transaction_ids=[], transaction_statuses=[],
               asset_book_ids=[], counterparty_book_ids=[], asset_ids=[], transaction_date_start=None,
               transaction_date_end=None, code_types=[], code_values=[], link_types=[], linked_transaction_ids=[],
               party_types=[], party_ids=[], reference_types=[], reference_values=[], client_ids=[]):
        self.logger.info('Search Transactions - Asset Manager(s): %s', asset_manager_ids)
        search_params = {}
        # Potentially roll this into a loop through args rather than explicitly named - depends on additional validation
        if asset_manager_ids:
            search_params['asset_manager_ids'] = ','.join([str(amid) for amid in asset_manager_ids])
        if transaction_ids:
            search_params['transaction_ids'] = ','.join(transaction_ids)
        if transaction_statuses:
            search_params['transaction_statuses'] = ','.join(transaction_statuses)
        if asset_book_ids:
            search_params['asset_book_ids'] = ','.join(asset_book_ids)
        if counterparty_book_ids:
            search_params['counterparty_book_ids'] = ','.join(counterparty_book_ids)
        if asset_ids:
            search_params['asset_ids'] = ','.join(asset_ids)
        if transaction_date_start:
            search_params['transaction_date_start'] = transaction_date_start
        if transaction_date_end:
            search_params['transaction_date_end'] = transaction_date_end
        if code_types:
            search_params['code_types'] = ','.join(code_types)
        if code_values:
            search_params['code_values'] = ','.join(code_values)
        if link_types:
            search_params['link_types'] = ','.join(link_types)
        if linked_transaction_ids:
            search_params['linked_transaction_ids'] = ','.join(linked_transaction_ids)
        if party_types:
            search_params['party_types'] = ','.join(party_types)
        if party_ids:
            search_params['party_ids'] = ','.join(party_ids)
        if reference_types:
            search_params['reference_types'] = ','.join(reference_types)
        if reference_values:
            search_params['reference_values'] = ','.join(reference_values)
        if client_ids:
            search_params['client_ids'] = ','.join(client_ids)
        url = self.endpoint + '/transactions'
        response = self.session.get(url, params=search_params)
        if response.ok:
            transactions = [json_to_transaction(json_transaction) for json_transaction in response.json()]
            self.logger.info('Returned %s Transactions.', len(transactions))
            return transactions
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def position_search(self, asset_manager_ids=None, book_ids=None, account_ids=None,
                        accounting_types=['Transaction Date'], asset_ids=None, position_date=None):
        self.logger.info('Search Positions - Asset Manager(s): %s', asset_manager_ids)
        url = self.endpoint + '/positions'
        search_params = {}
        # Potentially roll into a loop
        if asset_manager_ids:
            search_params['asset_manager_ids'] = ','.join([str(amid) for amid in asset_manager_ids])
        if book_ids:
            search_params['book_ids'] = ','.join(book_ids)
        if account_ids:
            search_params['account_ids'] = ','.join(account_ids)
        if accounting_types:
            search_params['accounting_types'] = ','.join(accounting_types)
        if asset_ids:
            search_params['asset_ids'] = ','.join(asset_ids)
        if position_date:
            search_params['position_date'] = position_date
        response = self.session.get(url, params=search_params)
        if response.ok:
            positions = [json_to_position(json_position) for json_position in response.json()]
            self.logger.info('Returned %s Positions.', len(positions))
            return positions
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    # Should this method just be collapsed into positions_by_asset_manager?
    def positions_by_asset_manager_book(self, asset_manager_id, book_id):
        self.logger.info('Retrieve Positions by Asset Manager: %s and Book: %s', asset_manager_id, book_id)
        url = '%s/positions/%s/%s' % (self.endpoint, asset_manager_id, book_id)
        response = self.session.get(url)
        if response.ok:
            positions = [json_to_position(json_position) for json_position in response.json()]
            self.logger.info('Returned %s Positions.', len(positions))
            return positions
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def positions_by_asset_manager(self, asset_manager_id, book_ids=None):
        self.logger.info('Retrieve Positions by Asset Manager: %s', asset_manager_id)
        url = '%s/positions/%s' % (self.endpoint, asset_manager_id)
        params = {'book_ids': ','.join(book_ids)} if book_ids else {}
        response = self.session.get(url, params=params)
        if response.ok:
            positions = [json_to_position(json_position) for json_position in response.json()]
            self.logger.info('Returned %s Positions.', len(positions))
            return positions
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def allocate_transaction(self, asset_manager_id, transaction_id, allocation_type, allocation_dicts):
        """

        :param asset_manager_id:
        :param transaction_id:
        :param allocation_type:
        :param allocation_dicts:
        :return:
        """
        self.logger.info('Allocate Transaction - Asset Manager: %s - Transaction ID: %s', asset_manager_id,
                         transaction_id)
        url = '%s/allocations/%s/%s' % (self.endpoint, asset_manager_id, transaction_id)
        params = {'allocation_type': allocation_type}
        response = self.session.post(url, params=params, data=json.dumps(allocation_dicts, default=json_handler),
                                     headers=self.json_header)
        if response.ok:
            allocations = [json_to_transaction(json_allocation) for json_allocation in response.json()]
            allocation_ids = [allocation.transaction_id for allocation in allocations]
            self.logger.info('%s Allocations Created - Transactions: %s', len(allocations), allocation_ids)
            return allocations
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve_transaction_allocations(self, asset_manager_id, transaction_id):
        """

        :param asset_manager_id:
        :param transaction_id:
        :return:
        """
        self.logger.info('Retrieve Allocations - Asset Manager: %s - Transaction ID: %s', asset_manager_id,
                         transaction_id)
        url = '%s/allocations/%s/%s' % (self.endpoint, asset_manager_id, transaction_id)
        response = self.session.get(url)
        if response.ok:
            allocations = [json_to_transaction(json_allocation) for json_allocation in response.json()]
            self.logger.info('Returned %s Allocations.', len(allocations))
            return allocations
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def net_transactions(self, asset_manager_id, transaction_ids, netting_type='Net'):
        """

        :param asset_manager_id: The asset_manager_id of the netting set owner
        :param transaction_ids:  A list of transaction_ids to net
        :param netting_type:
        :return:
        """
        self.logger.info('Net Transactions - Asset Manager: %s - Transaction IDs: %s', asset_manager_id,
                         transaction_ids)
        url = '%s/netting/%s' % (self.endpoint, asset_manager_id)
        params = {'netting_type': netting_type}
        response = self.session.post(url, params=params, json=transaction_ids)
        if response.ok:
            net_transaction = json_to_transaction(response.json())
            self.logger.info('Net Created - Transaction: %s', net_transaction.transaction_id)
            return net_transaction
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve_netting_set(self, asset_manager_id, transaction_id):
        """
        Returns all the transaction_ids associated with a single netting set.  Pass in the ID for any transaction in
        the set.
        :param asset_manager_id:  The asset_manager_id for the netting set owner.
        :param transaction_id: A transaction_id of an entry within the netting set.
        :return:
        """
        self.logger.info('Retrieve Netting Set - Asset Manager: %s - Transaction ID: %s', asset_manager_id,
                         transaction_id)
        url = '%s/netting/%s/%s' % (self.endpoint, asset_manager_id, transaction_id)
        response = self.session.get(url)
        if response.ok:
            net_transaction_id, netting_set_json = next(iter(response.json().items()))
            netting_set = [json_to_transaction(net_transaction) for net_transaction in netting_set_json]
            self.logger.info('Returned %s Transactions in Netting Set.', len(netting_set))
            return net_transaction_id, netting_set
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def upsert_transaction_asset(self, transaction_asset_json):
        """
        This API should not be called in normal circumstances as the asset cache will populate itself from the assets
        which are created via the Assets API.  However, it can be useful for certain testing scenarios.
        :param transaction_asset_json:
        :return:
        """
        url = self.endpoint + '/assets'
        response = self.session.post(url, json=transaction_asset_json)
        if response.ok:
            return response.json()
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def upsert_transaction_book(self, transaction_book_json):
        """
        This API should not be called in normal circumstances as the book cache will populate itself from the book
        which are created via the Books API.  However, it can be useful for certain testing scenarios.
        :param transaction_book_json:
        :return:
        """
        url = self.endpoint + '/books'
        response = self.session.post(url, json=transaction_book_json)
        if response.ok:
            return response.json()
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def book_transfer(self, asset_manager_id, asset_id, source_book_id, target_book_id, wash_book_id, quantity, price,
                      currency):
        """
        A method for moving between books.  The convention is always *from* the source, *to* the target.

        Two transactions are booked -  one against each

        :param asset_manager_id: The owning asset manager id.
        :param asset_id: The asset being transferred.
        :param source_book_id: The book id of the source.
        :param target_book_id:  The book id of the target.
        :param wash_book_id:  The book id of the wash book which will be the counterparty for the two sides.
        :param quantity: The quantity to transfer.
        :param price:  The price at which to make the transfer.  Typically T-1 EOD price or current market price.
        :param currency: The currency for the transfer price.
        :return:
        """
        url = '%s/book_transfer/%s' % (self.endpoint, asset_manager_id)
        body = {'asset_id': asset_id, 'source_book_id': source_book_id, 'target_book_id': target_book_id,
                'wash_book_id': wash_book_id, 'quantity': quantity, 'price': price, 'currency': currency}
        response = self.session.post(url, data=json.dumps(body, default=json_handler), headers=self.json_header)
        if response.ok:
            deliver_json, receive_json = response.json()
            return json_to_transaction(deliver_json), json_to_transaction(receive_json),
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def depot_transfer(self, asset_manager_id, asset_id, source_account_id, target_account_id, quantity):
        raise NotImplementedError("""This is not yet supported.  The concept is similar to a
                                  book transfer, except it requires an external message to a
                                  custodian to instruct them to move the stock to a
                                   different depot account.""")

    def clear(self, asset_manager_id, book_ids=None):
        """ This method deletes all the data for an asset_manager_id
            and option book_ids.
            It should be used with extreme caution.  In production it
            is almost always better to Inactivate rather than delete. """
        self.logger.info('Clear Transactions & Positions - Asset Manager: %s', asset_manager_id)
        url = '%s/clear/%s' % (self.endpoint, asset_manager_id)
        params = {'asset_manager_ids': ','.join(book_ids)} if book_ids else {}
        response = self.session.delete(url, params=params)
        if response.ok:
            tran_count = response.json().get('transaction_count', 'Unknown')
            self.logger.info('Deleted %s Transactions.', tran_count)
            pos_count = response.json().get('position_count', 'Unknown')
            self.logger.info('Deleted %s Positions.', pos_count)
            return response.json()
        else:
            self.logger.error(response.text)
            response.raise_for_status()
