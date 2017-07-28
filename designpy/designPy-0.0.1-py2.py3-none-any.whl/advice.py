class AdviceLevel:
	GOOD = 1
	MIXED = 2
	BAD = 3
	UNSURE = 4
	
class Advice(object):
	def __init__(self, adviceLevel, message, annotation = ""):
		self._adviceLevel = adviceLevel
		self._message = message
		self._annotation = annotation

	@property
	def adviceLevel(self):
		return self._adviceLevel
	
	@property
	def message(self):
		return self._message

	@property
	def annotation(self):
		return self._annotation