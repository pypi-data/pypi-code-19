# -*- coding: utf-8 -*-

"""
Client module with `Discoin()` class in
"""

import requests
from .errors import InvalidDiscoinToken, DiscoinError, TransactionNotFound
from .classes import Transaction, Conversion

class Discoin:
    """The main class used for interation with the Discoin API.

    :param token: The token given from Discoin developers to communicate with the API.
    :type token: str
    """
    def __init__(self, token):
        self.token = token
        self._headers = {"Authorization":self.token}
        self._transactions = []

    def make_transaction(self, user_id, amount, to):
        """Create a new transaction with the API

        :param user_id: The ID of the user who is making the exchange.
        :type user_id: int
        :param amount: The amount of local bot currency being exchanged
        :type amount: int
        :param to: The three letter currency code (e.g DTS, PYB) to exchange discoin to.
        :type to: str
        :returns: :class:`discoin.classes.Conversion`
        :raises: DiscoinError
        .. note:: Do not use Discoin as the amount currency. It should be the local amount of currency. The Discoin API will handle all conversions.
        """
        

        transaction_data = {
            "user": str(user_id),
            "amount": amount,
            "exchangeTo": to
        }

        res = requests.post("https://discoin.sidetrip.xyz/transaction", headers=self._headers, json=transaction_data)
        if res.status_code in [400,401,402,403,404,405]:
            raise DiscoinError(res.json()['reason'])


        return Conversion(self, res.json())

    def reverse_transaction(self, reciept):
        """Reverse an already made transaction.

        :param reciept: The reciept of the transaction to reverse.
        :type reciept: str
        :raises: DiscoinError
        """
        transaction_data = {
            "receipt": reciept
        }

        res = requests.post("https://discoin.sidetrip.xyz/transaction/reverse", headers=self._headers, json=transaction_data)
        if res.status_code in [400,401,402,403,404,405]:
            raise DiscoinError(res.json()['reason'])

        return None

    def get_transactions(self):
        """View all unprocessed transactions. Returns a list of :class:`discoin.classes.Transaction` classes.

        :returns: :class:`list`
        :raises: DiscoinError
        """
        res = requests.get("https://discoin.sidetrip.xyz/transactions", headers=self._headers)
        if res.status_code in [400,401,402,403,404,405]:
            raise DiscoinError(res.json()['reason'])

        transactions = []
        for transaction in res.json():
            transactions.append(Transaction(self, transaction.get('receipt')))
        return transactions

    def get_transaction(self, reciept):
        """Get info on a transaction.
        
        :param reciept: The reciept of the transaction.
        :type reciept: str
        :returns: :class:`discoin.classes.Transaction`
        :raises: DiscoinError
        """
        return Transaction(self, reciept)