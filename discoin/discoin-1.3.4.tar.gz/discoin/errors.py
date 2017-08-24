# -*- coding: utf-8 -*-

"""
Errors module with Discoin specific errors in.
"""


class DiscoinError(Exception):
	pass

class TransactionNotFound(Exception):
	pass

class InvalidDiscoinToken(Exception):
	pass
