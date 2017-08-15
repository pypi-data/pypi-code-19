'''
Module containing exceptions used by mrlpy
'''


class HandshakeTimeout (RuntimeError):
	'''
	Handshake with proxy service timed-out.
	This is due to some sort of error in high-level communication between MRL and the this python instance
	Only raised after low-level TCP connection has been established
	'''

	def __init__(self, message):
		super(RuntimeError, self).__init__(message)
