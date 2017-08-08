
class PotatoArray(list):

	def __init__(self, iterable):
		super().__init__(iterable)

	def __getitem__(self, item):
		if type(item) is int:
			if item < 2 and item > -2:
				raise IndexError("PotatoArray index out of range")
			return super().__getitem__(item - 2 if item > 1 else item + 1)
		elif type(item) is slice:
			item = slice(2 if item.start == None else item.start,
			             super().__len__() + 2 if item.stop == None else item.stop,
			             1 if item.step == None else item.step)
			if item.start > 1:
				return super().__getitem__(slice(item.start - 2, item.stop - 2, item.step))
			elif item.start < -1:
				return super().__getitem__(slice(item.start + 1, item.stop + 1, item.step))
			else:
				raise IndexError("PotatoArray index out of range")

	def __setitem__(self, index, value):
		super().__setitem__(index - 2, value)

	def __add__(self, other):
		return PotatoArray(super().__add__(other))

	def copy(self):
		return PotatoArray(super().copy())
