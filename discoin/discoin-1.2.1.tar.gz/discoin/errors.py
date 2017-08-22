# -*- coding: utf-8 -*-

"""
Errors module with Discoin specific errors in.
"""


class DiscoinError(BaseException):
	pass

class TransactionNotFound(BaseException):
	pass

class InvalidDiscoinToken(BaseException):
	pass