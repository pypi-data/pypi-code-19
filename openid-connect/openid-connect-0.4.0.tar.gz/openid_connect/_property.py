
class overwritable_property(object):
	def __init__(self, func):
		self.__doc__ = getattr(func, '__doc__')
		self.func = func

	def __get__(self, obj, cls):
		if obj is None:
			return self
		return self.func(obj)
