# -*- coding: utf-8 -*-

"""
Classes module with transaction classes in.
"""

import requests
import datetime
from .errors import *


class Amount:
    """A class showing currency amounts over the space of the transactions

    .. warning:: Do not attempt to construct this class yourself! It will not work!
    :ivar source: Amount of currency in source currency
    :ivar discoin: Amount of currency in Discoin
    :ivar target: Amount of currency once reached target bot
    """
    def __init__(self, dict_info):
        self.__dict__.update(dict_info)


class Transaction:
    """Transaction class, gets info on a transaction when created.

    .. warning:: Do not attempt to construct this class yourself! It will not work!
    :raises: InvalidDiscoinToken, TransactionNotFound
    """
    def __init__(self, discoin, reciept):
        self.discoin = discoin
        token = discoin.token
        headers = {"Authorization":token}
        info = requests.get("https://discoin.sidetrip.xyz/transaction/{}".format(reciept), headers=headers)
        if info.status_code == 404:
            raise TransactionNotFound("That transaction was not found")
        if info.status_code == 401:
            raise InvalidDiscoinToken("You have passed an invalid token to the Discoin Class")
        i = info.json()
        self.reciept = str(reciept) #: Reciept from transaction
        self.user = i.get("user") #: The user ID of the transaction
        self.timestamp = i.get("timestamp") #: Timestamp of transaction
        self.currency_from = i.get("source") #: Source currency of transaction
        self.currency_to = i.get("target") #: Target currency of transaction
        self.type = i.get("type") #: Type of transaction
        self.processed = i.get("processed") #: Has transaction been processed
        self.process_time = i.get("processTime") #: Time taken to process transaction
        amount_data = {
            "source": i.get("amountSource"),
            "discoin": i.get("amountDiscoin"),
            "target": i.get("amountTarget")
        }
        self.amount_info = Amount(amount_data) #: A :class:`discoin.classes.Amount` class with the information about amounts of currency varying during the transaction

    def __repr__(self):
        return "<Transaction '{}' to '{}' receipt '{}'>".format(self.currency_from, self.currency_to, self.reciept)

    def refund(self):
        """Refund the transaction. A helper function to execute :meth:`discoin.Discoin.reverse_transaction`

        :raises: DiscoinError
        """
        return self.discoin.reverse_transaction(self.reciept)


class Conversion:
    """Returned from make_transaction()

    .. warning:: Do not attempt to construct this class yourself! It will not work!
    """
    def __init__(self, discoin, data):
        self.status = data.get("status") #: Status of transaction
        self.receipt = data.get("receipt") #: Reciept of transaction
        self.limitNow = data.get("limitNow") #: Remaining limit for user
        self.resultAmount = data.get("resultAmount") #: Result amount of transaction
        self.discoin = discoin

    def get_info(self):
        """Get more info on a transaction
        
        :raises: InvalidDiscoinToken, TransactionNotFound
        :returns: :class:`discoin.classes.Transaction`
        """

        return Transaction(self.discoin, self.receipt)
