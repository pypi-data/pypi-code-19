# -*- coding: utf-8 -*-

"""
This file is part of datamatrix.

datamatrix is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

datamatrix is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with datamatrix.  If not, see <http://www.gnu.org/licenses/>.
---
desc: pass
---
"""

from datamatrix.py3compat import *
from datamatrix._datamatrix._index import Index
import collections
import numbers
import operator
import math
import warnings

INF = float('inf')
NAN = float('nan')

try:
	import fastnumbers
	
	def _sortkey(val):
		try:
			return fastnumbers.fast_float(val[0], default=INF, nan=INF)
		except TypeError:
			return INF

except ImportError:
	warnings.warn('Install fastnumbers for better performance')
	fastnumbers = None

	def _sortkey(val):
		
		try:
			val = float(val[0])
		except (ValueError, TypeError):
			return INF
		if math.isnan(val):
			return INF
		return val


class BaseColumn(object):

	"""
	desc:
		The base class for all columns. You should not use this class directly,
		but rather use MixedColumn or NumericColumn.
	"""

	default_value = u''

	def __init__(self, datamatrix):

		"""
		desc:
			Constructor.

		arguments:
			datamatrix:	A DataMatrix object.
		"""

		self._datamatrix = datamatrix
		self._typechecking = True
		self._init_rowid()
		self._init_seq()		

	@property
	def unique(self):

		"""
		name:	unique

		desc:
			An interator for all unique values that occur in the column.
		"""

		return list(safe_sorted(set(self._seq)))


	@property
	def count(self):

		"""
		name:	count

		desc:
			The number of unique values that occur in the column.
		"""

		return len(self.unique)


	@property
	def mean(self):

		"""
		name:	mean

		desc:
			Arithmetic mean of all values. If there are non-numeric values,
			these are ignored. If there are no numeric values, None or np.nan is
			returned.
		"""

		n = self._numbers
		if len(n) == 0:
			return NAN
		return sum(n) / len(n)

	@property
	def median(self):

		"""
		name:	median

		desc:
			The median of all values. If there are non-numeric values,
			these are ignored. If there are no numeric values, None or np.nan is
			returned.
		"""

		n = sorted(self._numbers)
		if len(n) == 0:
			return NAN
		i = int(len(n)/2)
		if len(n) % 2 == 1:
			return n[i]
		return .5*n[i]+.5*n[i-1]

	@property
	def std(self):

		"""
		name:	std

		desc:
			The standard deviation of all values. If there are non-numeric
			values, these are ignored. If there are 0 or 1 numeric values, None
			or np.nan is returned. The degrees of freedom are N-1.
		"""

		m = self.mean
		n = self._numbers
		if len(n) <= 1:
			return NAN
		return math.sqrt(sum((i-m)**2 for i in n)/(len(n)-1))

	@property
	def max(self):

		"""
		name:	max

		desc:
			The highest numeric value in the column, or None or np.nan if there
			are no numeric values.
		"""

		n = self._numbers
		if not len(n):
			return NAN
		return max(n)

	@property
	def min(self):

		"""
		name:	min

		desc:
			The lowest numeric value in the column, or None or np.nan if there
			are no numeric values.
		"""

		n = self._numbers
		if not len(n):
			return NAN
		return min(n)

	@property
	def sum(self):

		"""
		name:	sum

		desc:
			The sum of all values in the column, or None or np.nan if there
			are no numeric values.
		"""

		n = self._numbers
		if not len(n):
			return NAN
		return sum(n)

	@property
	def name(self):
		
		"""
		name:	name

		desc:
			The name of the column in the associated DataMatrix, or a
			list of names if the column occurs multiple times in the DataMatrix.
		"""

		l = [name for name, col in self._datamatrix.columns if col is self]
		if not l:
			raise NameError(
				u'Column not found in DataMatrix, and therefore nameless')
		if len(l) == 1:
			return l[0]
		return l
			
	@property
	def dm(self):
		
		"""
		name:	dm

		desc:
			The associated DataMatrix.
		"""		
		
		return self._datamatrix

	# Private functions

	@property
	def _numbers(self):

		return [float(val) for val in self._seq \
			if isinstance(val, numbers.Number) and not self._nanorinf(val)]

	def _printable_list(self):

		"""
		visible: False

		desc:
			Creates a list object for this column. The preferred syntax is
			list(dm), although this is slightly slower.

		returns:
			type:	list
		"""

		return self._seq

	def _init_rowid(self):

		"""
		visible: False

		desc:
			Intializes the _rowid property, which is an iterator that contains
			the row ids.
		"""

		self._rowid = self._datamatrix._rowid.clone()

	def _init_seq(self):

		"""
		visible: False

		desc:
			Initializes the _seq property, which is an iterator that contains
			the data.
		"""

		self._seq = [self.default_value]*len(self._datamatrix)

	def _addrowid(self, _rowid):

		"""
		visible: False

		desc:
			Adds an empty row with the given row id.

		arguments:
			_rowid:	A row id
		"""

		self._rowid += _rowid
		self._seq += [self.default_value]*len(_rowid)

	def _checktype(self, value):

		"""
		visible: False

		desc:
			Checks wether a value has a suitable type for this column, converts
			it if possible, and gives an error if necessary.

		arguments:
			value:	A value to check.

		returns:
			A suitably typed value.
		"""
		
		if value is None:
			return value
		if fastnumbers is not None:
			value = fastnumbers.fast_real(value, nan=NAN, inf=INF)
		else:
			try:
				assert(int(value) == value)
				value = int(value)
			except:
				try:
					# Make sure we don't convert 'inf' and 'nan' strings to float
					assert(not math.isinf(float(value)))
					assert(not math.isnan(float(value)))
					value = float(value)
				except:
					pass
		if isinstance(value, (int, float, str)):
			return value
		if isinstance(value, bytes):
			return safe_decode(value)
		raise TypeError('Invalid type: %s' % value)

	def _merge(self, other, _rowid):

		"""
		visible: False

		desc:
			Merges this column with another column, selecting only the rows
			indicated by _rowid.

		arguments:
			other:	Another column.
			_rowid:	A list of row ids to select.

		returns:
			type: BaseColumn
		"""

		col = self._empty_col()
		col._rowid = _rowid
		col._seq = []
		for row in _rowid:
			if row in self._rowid:
				col._seq.append(self._seq[self._rowid.index(row)])
			else:
				col._seq.append(other._seq[other._rowid.index(row)])
		return col

	def _tosequence(self, value, length=None):

		"""
		visible: False

		desc:
			Creates a sequence with a specific length from a given value (which
			may already be a sequence).

		arguments:
			value:	The value to turn into a sequence.
			
		keywords:
			length:	The length of the sequence, or None to use length of\
					DataMatrix.

		returns:
			A sequence, that is, some iterable object.
		"""

		if length is None:
			length = len(self._datamatrix)
		if value is None or isinstance(value, (numbers.Number, basestring)):
			return [self._checktype(value)]*length
		try:
			value = list(value)
		except:
			raise Exception('Cannot convert to sequence: %s' % value)
		if len(value) != length:
			raise Exception('Sequence has incorrect length: %s' % len(value))
		return [self._checktype(cell) for cell in value]

	def _getintkey(self, key):

		"""
		visible: False

		desc:
			Gets a value by index.

		arguments:
			key:	An index.

		returns:
			A value.
		"""

		return self._seq[key]

	def _getslicekey(self, key):

		"""
		visible: False

		desc:
			Gets a slice of this column by a slice object.

		arguments:
			key:	A slice object.

		returns:
			BaseColunn
		"""

		col = self._empty_col()
		col._rowid = self._rowid[key]
		col._seq = self._seq[key]
		return col

	def _getsequencekey(self, key):

		"""
		visible: False

		desc:
			Gets a slice of this column by list or some other iterable.

		arguments:
			key:	A list or other iterable object.

		returns:
			BaseColunn
		"""

		col = self._empty_col()
		col._rowid = Index()
		col._seq = []
		for i in key:
			col._rowid.append(self._rowid[i])
			col._seq.append(self._seq[i])
		return col

	def _getrowidkey(self, key):

		"""
		visible: False

		desc:
			Gets a slice of this column by a list of row ids.

		arguments:
			key:	A list of row ids.

		returns:
			BaseColunn
		"""

		col = self._empty_col()
		col._rowid = key
		col._seq = [self._seq[self._rowid.index(_rowid)] for _rowid in key]
		return col

	def _sortedrowid(self):

		"""
		visible: False

		desc:
			Gives a list of rowids that are ordered such that they sort the
			column.

		returns:
			An iterator.
		"""

		try:
			s = sorted(zip(self._seq, self._rowid))
		except:
			warn('Cannot sorted incomparable types. Forcing all values to float.')
			s = sorted(zip(self._seq, self._rowid), key=_sortkey)
		return Index([rowid for val, rowid in s])

	def _setintkey(self, key, value):

		"""
		visible: False

		desc:
			Sets a value by index.

		arguments:
			key:	An index.
			value:	The value to set.
		"""

		self._seq[key] = self._checktype(value)

	def _setslicekey(self, key, value):

		"""
		visible: False

		desc:
			Sets a range of values by a slice object.

		arguments:
			key:	A slice object.
			value:	The value to set. This can be an iterable that matches the
					length of the slice.
		"""

		# If type-checking is disabled and we're receiving a BaseColumn, assign
		# right away to speed up performance
		if not self._typechecking and type(value) == type(self):
			self._seq[key] = value._seq
			return
		length = len(self._seq[key])
		self._seq[key] = self._tosequence(value, length)

	def _setsequencekey(self, key, val):

		"""
		visible: False

		desc:
			Sets a range of values by a list or other iterable.

		arguments:
			key:	A list or other iterable object.
			val:	The value to set. This can be an iterable that matches the
					length of the key.
		"""

		for _key, _val in zip(key, self._tosequence(val, len(key))):
			if _key < 0 or _key >= len(self):
				raise Exception('Outside of range')
			self._seq[_key] = _val
			
	def _issequence(self, val):
		
		if isinstance(val, basestring) or not hasattr(val, u'__len__'):
			return False
		if len(val) != len(self._datamatrix):
			raise TypeError(u'Sequence has invalid length')
		return True

	def _compare(self, other, op):

		"""
		visible: False

		desc:
			Selects rows from this column, and returns the entire DataMatrix.

		arguments:
			other:	A value to compare to.
			op:		An operator to perform the comparison.

		returns:
			type:	DataMatrix
		"""

		if isinstance(other, type):
			return self._compare_type(other, op)
		if self._issequence(other):
			return self._compare_sequence(other, op)
		return self._compare_value(other, op)
		
	def _compare_type(self, type_, op):
		
		_rowid = Index(0)
		if op is operator.eq:
			for rowid, val in zip(self._rowid, self._seq):
				if isinstance(val, type_):
					_rowid.append(rowid)
		elif op is operator.ne:
			for rowid, val in zip(self._rowid, self._seq):
				if not isinstance(val, type_):
					_rowid.append(rowid)
		else:
			raise TypeError('types can only be compared with == or !=')
		return self._datamatrix._selectrowid(_rowid)		
		
	def _compare_value(self, other, op):

		_rowid = Index(0)
		for rowid, val in zip(self._rowid, self._seq):
			try:
				if op(val, other):
					_rowid.append(rowid)
			except:
				pass
		return self._datamatrix._selectrowid(_rowid)
		
	def _compare_sequence(self, other, op):
		
		_rowid = Index(0)
		for rowid, val, ref in \
				zip(self._rowid, self._seq, self._tosequence(other)):
			try:
				if op(val, ref):
					_rowid.append(rowid)
			except:
				pass
		return self._datamatrix._selectrowid(_rowid)				

	def _operate(self, other, number_op, str_op=None):

		"""
		visible: False

		desc:
			Performs an operation on the entire column.

		arguments:
			other:		The value to use for the operation, e.g. a number to
						multiply with.
			number_op:	The operator to use for numeric values.

		keywords:
			str_op:		The operator to use for string values, or None to
						leave strings untouched.

		returns:
			A modified column.
		"""

		col = self._empty_col()
		col._rowid = self._rowid
		col._seq = []
		for i, (_other, val) in enumerate(
			zip(self._tosequence(other, len(self)), self._seq)):
			if isinstance(val, numbers.Number) \
				and isinstance(_other, numbers.Number):
				col._seq.append(number_op(self._seq[i], _other))
			elif str_op is not None:
				col._seq.append(str_op(safe_decode(self._seq[i]),
					safe_decode(_other)))
			else:
				col._seq.append(self._seq[i])
		return col

	def _empty_col(self):

		"""
		visible: False

		desc:
			Create an empty column of the same type as the current column.

		returns:
			BaseColumn
		"""

		return self.__class__(self._datamatrix)
		
	def _nanorinf(self, val):
		
		"""
		visible: False
		
		desc:
			Checks whether a value is nan or inf.
			
		returns:
			bool
		"""
		
		return val != val or val == INF
		
	# Implemented syntax

	def __str__(self):

		return u'col%s' % str(self._seq)
		
	def __repr__(self):
		
		return u'%s[0x%x]\n%s' % (self.__class__.__name__, id(self), str(self))

	def __len__(self):

		return len(self._seq)

	def __getitem__(self, key):

		if isinstance(key, int):
			return self._getintkey(key)
		if isinstance(key, slice):
			return self._getslicekey(key)
		if isinstance(key, collections.Sequence):
			return self._getsequencekey(key)
		raise Exception(u'Invalid key')

	def __setitem__(self, key, value):

		if isinstance(key, int):
			self._setintkey(key, value)
		elif isinstance(key, slice):
			self._setslicekey(key, value)
		elif isinstance(key, collections.Sequence):
			self._setsequencekey(key, value)
		else:
			raise Exception('Invalid assignment')
		self._datamatrix._mutate()

	def __gt__(self, other):
		return self._compare(other, operator.gt)
	def __ge__(self, other):
		return self._compare(other, operator.ge)
	def __lt__(self, other):
		return self._compare(other, operator.lt)
	def __le__(self, other):
		return self._compare(other, operator.le)
	def __eq__(self, other):
		return self._compare(other, operator.eq)
	def __ne__(self, other):
		return self._compare(other, operator.ne)
	def __add__(self, other):
		return self._operate(other, operator.add, operator.concat)
	def __sub__(self, other):
		return self._operate(other, operator.sub)
	def __mul__(self, other):
		return self._operate(other, operator.mul)
	def __div__(self, other):
		return self._operate(other, operator.truediv)
	def __truediv__(self, other):
		return self._operate(other, operator.truediv)
	def __floordiv__(self, other):
		return self._operate(other, operator.floordiv)
	def __mod__(self, other):
		return self._operate(other, operator.mod)
	def __pow__(self, other):
		return self._operate(other, operator.pow)
	
