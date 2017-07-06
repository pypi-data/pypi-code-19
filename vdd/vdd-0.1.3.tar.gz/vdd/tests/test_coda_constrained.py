#import unittest
#
#from ddt import data, unpack, ddt
#
#from vdd import coda_constrained as coda
#
#
#
#class DummyCharacteristic(coda.BaseCharacteristic):
#	pass
#
#
#class DummyRequirement(coda.BaseRequirement):
#	pass
#
#
#@ddt
#class TestCODA(unittest.TestCase):
#
#	def setUp(self):
#		self.inst = coda.CODA()
#		self.inst.requirements = tuple([DummyRequirement()
#									   for i in 1,2,3,4])
#		self.inst.characteristics = tuple([DummyCharacteristic()
#										   for i in 1,2,3,4,5])
#
#	def test_array__unset(self):
#		"""Array should reflect shape and contain CODANull by default.
#		"""
#		temp_inst = coda.CODA()
#		self.assertEqual(temp_inst.array.shape, (0, 0))
#
#		self.assertEqual(self.inst.array.shape, (4, 5))
#
#		self.inst.requirements += (DummyRequirement(),)
#		self.assertEqual(self.inst.array.shape, (5, 5))
#
#		for i, j in zip(*map(range, self.inst.array.shape)):
#			self.assertIsInstance(self.inst.array[i,j], coda.CODANull)
#
#	def test_characteristics__default(self):
#		"""Should be an empty tuple by default."""
#		temp_inst = coda.CODA()
#		self.assertIsInstance(temp_inst.characteristics, tuple)
#		self.assertEqual(len(temp_inst.characteristics), 0.0)
#		self.assertEqual(len(self.inst.requirements), 4)
#
#	@data([(DummyCharacteristic(),), True],
#		  [(DummyRequirement(),), False],
#		  [(0,), False],
#		  [[0,], False],
#		  [0, False],
#		  [DummyCharacteristic(), False])
#	@unpack
#	def test_characteristics__set(self, value, valid):
#		"""Tuple of characteristics is enforced."""
#		# TODO: Currently, we should enforce that the new tuple is an
#		# extension of the old one otherwise everything breaks.
#		if valid:
#			self.inst.characteristics = value
#			self.assertEqual(self.inst.characteristics, value)
#		else:
#			self.assertRaises(ValueError, setattr, self.inst,
#							  'characteristics', value)
#
#	def test_requirements__default(self):
#		"""Should be an empty tuple by default."""
#		temp_inst = coda.CODA()
#		self.assertIsInstance(temp_inst.characteristics, tuple)
#		self.assertEqual(len(temp_inst.characteristics), 0.0)
#		self.assertEqual(len(self.inst.requirements), 4)
#
#	@data([(DummyCharacteristic(),), False],
#		  [(DummyRequirement(),), True],
#		  [(0,), False],
#		  [[0,], False],
#		  [0, False],
#		  [DummyRequirement(), False])
#	@unpack
#	def test_requirements__set(self, value, valid):
#		"""Tuple of requirements is enforced."""
#		# TODO: Currently, we should enforce that the new tuple is an
#		# extension of the old one otherwise everything breaks.
#		if valid:
#			self.inst.requirements = value
#			self.assertEqual(self.inst.requirements, value)
#		else:
#			self.assertRaises(ValueError, setattr, self.inst,
#							  'requirements', value)
#
#	def test_shape(self):
#		"""Shape should reflect the characteristics & requirements."""
#		self.assertEqual(self.inst.shape, (4, 5))
#
#
#@ddt
#class TestCODARelationship(unittest.TestCase):
#
#	def setUp(self):
#		class Concrete(coda.CODARelationship):
#			def __init__(self):
#				pass
#
#			def __call__(self, x):
#				return 0.0
#
#		self.cls = Concrete
#		self.inst = Concrete()
#
#	@data([0.0, True],
#		  [0.1, True],
#		  [0.3, True],
#		  [0.9, True],
#		  [1.0, False],
#		  [0.25, False],
#		  [-0.1, False],
#		  [0, True],
#	)
#	@unpack
#	def test_correlation(self, value, valid):
#		"""Correlation value must be one of a restricted set."""
#		# TODO: It might be more flexible to enforce this further up
#		#		for different scaling systems.
#		self.assertRaises(AttributeError, getattr, self.inst,
#						  'correlation')
#		if valid:
#			self.inst.correlation = value
#			self.assertEqual(self.inst.correlation, value)
#		else:
#			self.assertRaises(ValueError, setattr, self.inst,
#							  'correlation', value)
#
#	def test_target(self):
#		"""Target value may be anything, but check it's settable."""
#		self.assertRaises(AttributeError, getattr, self.inst,
#						  'target')
#		self.inst.target = 0.0
#		self.assertEqual(self.inst.target, 0.0)
#
#
#class TestCODANull(unittest.TestCase):
#
#	def test___init__(self):
#		"""Takes no arguments, has a correlation and merit of zero."""
#		null = coda.CODANull()
#		self.assertEqual(null.correlation, 0.0)
#		self.assertIs(null.target, None)
#		self.assertEqual(null(None), 0.0)
#
#	def test__attributes_not_settable(self):
#		null = coda.CODANull()
#
#		self.assertRaises(TypeError, setattr, null, 'correlation', 1)
#		self.assertRaises(TypeError, setattr, null, 'target', 1)
