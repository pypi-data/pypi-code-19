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
import datetime
from .errors import *


class Amount:
	def __init__(self, dict_info):
		self.__dict__.update(dict_info)


class Transaction:
	"""
	Transaction class, gets info on a transaction when created.
	"""
	def __init__(self, discoin, reciept):
		token = discoin.token
		headers = {"Authorization":token}
		info = requests.get("https://discoin.sidetrip.xyz/transaction/{}".format(reciept), headers=headers)
		if info.status_code == 404:
			raise TransactionNotFound("That transaction was not found")
		if info.status_code == 401:
			raise InvalidDiscoinToken("You have passed an invalid token to the Discoin Class")
		i = info.json()
		self.reciept = reciept
		self.user = i.get("user")
		self.timestamp = i.get("timestamp")
		self.currency_from = i.get("source")
		self.currency_to = i.get("target")
		self.type = i.get("type")
		self.processed = i.get("processed")
		self.process_time = i.get("process_time")
		amount_data = {
		    "source": i.get("amount_source"),
		    "discoin": i.get("amount_discoin"),
		    "target": i.get("amount_target")
		}
		self.amount_info = Amount(amount_data)

	def __repr__(self):
		return "<Transaction '{}' to '{}' receipt '{}'>".format(self.currency_from, self.currency_to, self.reciept)

class Conversion:
	"""
	Returned from make_transaction()
	"""
	def __init__(self, discoin, data):
		print(data)
		self.status = data.get("status")
		self.receipt = data.get("receipt")
		self.limitNow = data.get("limitNow")
		self.resultAmount = data.get("resultAmount")
		self.discoin = discoin

	def get_info(self):
		return Transaction(self.discoin, self.receipt)