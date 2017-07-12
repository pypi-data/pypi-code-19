"""Helper utils for the bitarray module.

bautils contains a handful of helper functions for bitarray. Most noticeably,
the bautils.add routine allows you to add two bitarrays together as if they
were binary numbers.

There are also routines to enable converting back and forth from bitarrays
to bitstrings (a similar Python module).
"""

import bitarray
import bitstring
import random as _random

def addBits(b1, b2):
	"""	Helper function, implementing a binary adder for bits b1, b2."""
	result = b1 ^ b2
	carry = b1 & b2
	return result, carry

def add(b1, b2):
	"""	Adds two bitarrays of arbitrary size using binary addition, and returns the result."""

	# If the bitarrays aren't the same length, expand them so they are.
	if b1.length() != b2.length():
		maxLength = max(b1.length(), b2.length())
		b1 = bitarray.bitarray('0' * (maxLength - b1.length())) + b1
		b2 = bitarray.bitarray('0' * (maxLength - b2.length())) + b2

	# Add another bit to the ends.
	b1 = bitarray.bitarray('0') + b1
	b2 = bitarray.bitarray('0') + b2

	# Loop over all bits, compute result and carry.
	for i in range(b1.length() - 1, 0, -1):
		result, carry = addBits(b1[i], b2[i])
		b1[i] = result
		j = i
		while carry != 0:
			j -= 1
			result, carry = addBits(b1[j], carry)
			b1[j] = result


	# Remove leading zero, if it exists.
	if b1[0] == 0:
		b1.remove(0)

	return b1

def left(ba, n):
	"""	Shift a bitarray ba left by n. Does not change size of ba."""
	length = ba.length()
	shifted = ba + bitarray.bitarray(n * '0')
	return shifted[n:]

def right(ba, n):
	"""	Shift a bitarray ba right by n."""
	length = ba.length()
	shifted = bitarray.bitarray(n * '0') + ba
	return shifted[:length]

def random(length, seed=None):
	"""	Returns a random bitarray of size length, using random module."""
	_random.seed()
	ba = bitarray.bitarray()
	for i in range(length):
		ba += bitarray.bitarray('%d' % _random.randint(0, 1))
	return ba

def maxb(b1, b2):
	"""	Computes the maximum of b1 and b2, and returns the max in bitarray form. Returns b1 if results are equal."""
	# If the bitarrays aren't the same length, expand them so they are.
	if b1.length() != b2.length():
		maxLength = max(b1.length(), b2.length())
		b1 = bitarray('0' * (maxLength - b1.length())) + b1
		b2 = bitarray('0' * (maxLength - b2.length())) + b2

	# Finds the first MSB that differs.
	for i in range(len(b1)):
		if b1[i] > b2[i]:
			return b1
		elif b1[i] < b2[i]:
			return b2

	# Returns b1 if they are equal.
	return b1

def minb(b1, b2):
	"""	Computes the minimum of b1 and b2, and returns the min in bitarray form. Returns b1 if results are equal."""
	# If the bitarrays aren't the same length, expand them so they are.
	if b1.length() != b2.length():
		maxLength = max(b1.length(), b2.length())
		b1 = bitarray('0' * (maxLength - b1.length())) + b1
		b2 = bitarray('0' * (maxLength - b2.length())) + b2

	# Finds the first MSB that differs.
	for i in range(len(b1)):
		if b1[i] > b2[i]:
			return b2
		elif b1[i] < b2[i]:
			return b1

	# Returns b1 if they are equal.
	return b1

def toBits(ba):
	"""	Takes a bitarray and returns a corresponding bitstring.Bits."""
	return bitstring.Bits(bin=ba.to01())

def toBitArray(ba):
	"""	Takes a bitarray and returns a corresponding bitstring.BitArray."""
	return bitstring.BitArray(bin=ba.to01())

def toConstBitStream(ba):
	"""	Takes a bitarray and returns a corresponding bitstring.ConstBitStream."""
	return bitstring.ConstBitStream(bin=ba.to01())

def toBitStream(ba):
	"""	Takes a bitarray and returns a corresponding bitstring.BitStream."""
	return bitstring.BitStream(bin=ba.to01())

def fromBitString(bs):
	"""	Takes a bitstring type and returns a corresponding bitarray."""
	return bitarray.bitarray(bs.bin)
