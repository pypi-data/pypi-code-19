from __future__ import absolute_import

from .module import Zymkey

__all__ = ['Zymkey', 'client']

try:
	client = Zymkey()
except  AssertionError:
	client = None
	pass
