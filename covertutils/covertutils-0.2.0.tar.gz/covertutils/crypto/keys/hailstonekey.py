# from covertutils.crypto.keys import CyclingKey, EncryptionKey
#
# from covertutils.helpers import sxor
#
# from covertutils.crypto.algorithms import StandardCyclingAlgorithm
#
# from struct import unpack
#
#
# class HailstoneCyclingKey( CyclingKey, EncryptionKey ) :
#
#
# 	def __init__( self, passphrase, cycling_algorithm = None, salt = None, **kw ) :
# 		self.__counter = 0
# 		self.cycling_algorithm = cycling_algorithm
# 		if self.cycling_algorithm == None:
# 			self.cycling_algorithm = StandardCyclingAlgorithm
#
# 		if salt != None :
# 			self.__salt = salt
# 		self.initial_key = self.__createKey( passphrase )
# 		self.reset()
#
# 		del(passphrase)	# just to be sure
#
#
#
# 	def cycle
