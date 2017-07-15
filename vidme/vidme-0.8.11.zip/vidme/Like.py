
import api

from User import User

class Like:

	def __init__(self, meta):
		self.set_meta(meta)

	def set_meta(self, meta):
		# Confirm meta is good
		self.meta = meta

		for key, value in meta.items():
			if key == 'user':
				value = User(meta={'user': value})

			# Add item to class
			setattr(self, key, value)
			# Add getter for item
			setattr(self, 'get_' + key, lambda k=key: self._get_safe(k))

	def _get_safe(self, name):
		if hasattr(self, name):
			return getattr(self, name)
		else:
			return False
