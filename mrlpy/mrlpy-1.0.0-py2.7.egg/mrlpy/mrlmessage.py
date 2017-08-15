from mrlpy.mevent import MEvent
import logging

"""Subclass of MEvent, used to represent MRL messages"""
class MrlMessage(MEvent):
	name = ""
	method = ""
	data = []	
	log = logging.getLogger(__name__)

	def __init__(self, name, method, dat):
		self.log.debug("Creating message structure")
		self.name = name
		self.log.debug("Name set: " + name)
		self.method = method
		self.log.debug("Method set: " + method)
		self.data = dat
		self.log.debug("Data set" )
		super(MrlMessage, self).__init__(name)
