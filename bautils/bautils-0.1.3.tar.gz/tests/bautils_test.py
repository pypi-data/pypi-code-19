# Unit tests for python-bautils.

import unittest

import bitarray
import bautils

class TestBAUtils(unittest.TestCase):

	def test_addition(self):
		"""	Test that binary addition behaves as expected."""
		b1 = bitarray.bitarray('01010')
		b2 = bitarray.bitarray('10101')
		b3 = bautils.add(b1, b2)
		self.assertEqual(b3, bitarray.bitarray('11111'))

		b4 = bautils.add(b3, b1)
		self.assertEqual(b4, bitarray.bitarray('101001'))

	def test_addition_different_sizes(self):
		"""	Test that we can add bitarrays of different sizes properly."""
		b1 = bitarray.bitarray('01')
		b2 = bitarray.bitarray('100')
		b3 = bautils.add(b1, b2)
		b4 = bautils.add(b2, b1)

		self.assertEqual(b3, bitarray.bitarray('101'))
		self.assertEqual(b4, bitarray.bitarray('101'))

	def test_left_shift(self):
		"""	Test that shifting a bitarray to the left behaves as expected."""
		b1 = bitarray.bitarray('01010')
		b2 = bautils.left(b1, 1)
		self.assertEqual(b2, bitarray.bitarray('10100'))

		b3 = bautils.left(b1, 5)
		self.assertEqual(b3, bitarray.bitarray('00000'))

	def test_right_shift(self):
		"""	Test that shifting a bitarray to the right behaves as expected."""
		b1 = bitarray.bitarray('01010')
		b2 = bautils.right(b1, 1)
		self.assertEqual(b2, bitarray.bitarray('00101'))

		b3 = bautils.right(b1, 5)
		self.assertEqual(b3, bitarray.bitarray('00000'))

	def test_random_bitarray_length(self):
		"""	Test that we can generate a random bitarray of arbitrary length."""
		b1 = bautils.random(10)
		self.assertEqual(b1.length(), 10)

		b2 = bautils.random(1)
		self.assertEqual(b2.length(), 1)

		b3 = bautils.random(0)
		self.assertEqual(b3.length(), 0)

		b3 = bautils.random(-1)
		self.assertEqual(b3.length(), 0)

	def test_min_max_bitarrays(self):
		"""	Test that we can compute the minimum and maximum of bitarrays."""
		b1 = bitarray.bitarray('0101')
		b2 = bitarray.bitarray('0001')

		b_max = bautils.maxb(b1, b2)
		b_min = bautils.minb(b1, b2)

		self.assertEqual(b1, b_max)
		self.assertEqual(b2, b_min)

if __name__ == '__main__':
	unittest.main()
