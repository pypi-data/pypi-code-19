# -*- coding: utf-8 -*-

"""
The MIT License (MIT)
Copyright (c) 2015-2016 Rapptz
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import requests
from .errors import InvalidDiscoinToken, DiscoinError, TransactionNotFound
from .classes import Transaction, Conversion

class Discoin:
    def __init__(self, token):
        self.token = token
        self._headers = {"Authorization":self.token}
        self._transactions = []

    def make_transaction(self, user_id, amount, to):

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
        transaction_data = {
            "receipt": reciept
        }

        res = requests.post("https://discoin.sidetrip.xyz/transaction/reverse", headers=self._headers, json=transaction_data)
        if res.status_code in [400,401,402,403,404,405]:
            raise DiscoinError(res.json()['reason'])

        return None

    def get_transactions(self):
        res = requests.get("https://discoin.sidetrip.xyz/transactions", headers=self._headers)
        if res.status_code in [400,401,402,403,404,405]:
            raise DiscoinError(res.json()['reason'])

        transactions = []
        for transaction in res.json():
            transactions.append(Transaction(self, transaction.get('receipt')))
        return transactions

    def get_transaction(self, reciept):
        return Transaction(self, reciept)