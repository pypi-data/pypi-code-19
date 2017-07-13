# Unit tests for python-bautils.
# Tests conversion from bitarrays to bitstrings.

import unittest

import bitstring
import bitarray
import bautils

class TestBitarrayBitstring(unittest.TestCase):

	def test_bitarray_bits(self):
		b1 = bitarray.bitarray('1010')
		expected = bitstring.Bits(bin='1010')

		stream = bautils.toBits(b1)
		self.assertEqual(stream, expected)
		b2 = bautils.fromBitString(stream)
		self.assertEqual(b1, b2)

	def test_bitarray_bitarray(self):
		b1 = bitarray.bitarray('1010')
		expected = bitstring.BitArray(bin='1010')

		stream = bautils.toBitArray(b1)
		self.assertEqual(stream, expected)
		b2 = bautils.fromBitString(stream)
		self.assertEqual(b1, b2)

	def test_bitarray_constbitstring(self):
		b1 = bitarray.bitarray('1010')
		expected = bitstring.ConstBitStream(bin='1010')

		stream = bautils.toConstBitStream(b1)
		self.assertEqual(stream, expected)
		b2 = bautils.fromBitString(stream)
		self.assertEqual(b1, b2)

	def test_bitarray_bitstring(self):
		b1 = bitarray.bitarray('1010')
		expected = bitstring.BitStream(bin='1010')

		stream = bautils.toBitStream(b1)
		self.assertEqual(stream, expected)
		b2 = bautils.fromBitString(stream)
		self.assertEqual(b1, b2)

if __name__ == '__main__':
	unittest.main()
