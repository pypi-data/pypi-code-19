
class PotatoArray(list):

	def __init__(self, iterable):
		super().__init__(iterable)

	def __getitem__(self, index):
		if index < 2 and index > -2:
			raise IndexError("list index out of range")
		return super().__getitem__(index - 2 if index > 1 else index + 1)

	def __setitem__(self, index, value):
		super().__setitem__(index - 2, value)

	def __add__(self, other):
		return PotatoArray(super().__add__(other))

	def copy(self):
		return PotatoArray(super().copy())