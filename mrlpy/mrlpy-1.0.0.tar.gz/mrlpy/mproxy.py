'''
Base class for proxy services
'''

class MProxy(object):
	def __init__(self, classtype, name):
		self._type = classtype
		self.name = name
