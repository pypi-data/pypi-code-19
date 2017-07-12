import numpy as np
from .utils import reverser, checkBroadcast

class ArrayFunc(object):
	'''
	An ArrayFunc is a function which accepts as input a numpy array of shape (dim, ...)
	and returns a numpy array of shape (s0, s1, ..., sk, ...) which vectorizes over
	all but the first index of its input.

	ArrayFuncs override multiplication to return the function representing the outer product
	of the non-vectorized parts of the function.

	ArrayFuncs are intended to, wherever possible, act as lazily-evaluated numpy arrays.
	'''

	def __init__(self, func, shape, dim, name=None):
		'''
		An ArrayFunc requires:
			func 	-	A function matching the description above.
			shape 	-	The shape of the output of the function,
						neglecting the vectorized axes.
			dim 	-	The length of the first dimension of the input
						to the function.
			name	-	An identifier which is useful for debug purposes.
		'''

		self.func = func
		self.dim = dim

		self.shape = list(shape)
		self.rank = len(shape)

		if name is None:
			self.name = 'func'
		else:
			self.name = name

	def __str__(self):
		return self.name

	def __call__(self, x):
		'''
		Allows a ArrayFunc to be called like a regular function.
		'''

		if len(x) != self.dim:
			raise ValueError

		ret = self.func(x)
		assert tuple(self.shape) == tuple(ret.shape[:self.rank])

		return ret

	def __len__(self):
		'''
		Allows an ArrayFunc to have the attribute len, such that
		len(f) == f.shape[0].
		'''
		return self.shape[0]

	def __mul__(self, other):
		'''
		Overrides multiplication.

		If other is a number or numpy array this multiplies
		the function by it, using a tensor product for arrays.
		Otherwise other must be an ArrayFunc, in which case the
		new function is the tensor product of self and other
		along all but the coordinate axes, and so has shape
		self.shape + other.shape.
		'''

		if hasattr(other, 'func'):
			if self.dim != other.dim:
				raise ValueError

			def f(x):
				# Flatten input
				inflat, sh, _ = self.flattenInput(x)

				# Flatten functions
				sf = self.flat
				of = other.flat

				# Compute output
				rS = sf(inflat)
				rO = of(inflat)

				# Combine output
				ret = rS[:,np.newaxis,:] * rO[np.newaxis,:,:]

				# Put it back in the correct shape
				ret = np.reshape(ret, self.shape + other.shape + sh)

				return ret

			name = '(' + self.name + ' * ' + other.name +')'
			return ArrayFunc(f, self.shape + other.shape, self.dim, name=name)
		elif hasattr(other, 'shape'):
			def f(x):
				# Flatten input
				inflat, sh, _ = self.flattenInput(x)

				# Flatten functions
				sf = self.flat

				# Compute output
				rS = sf(inflat)
				rO = other.flatten()

				# Combine output
				ret = rS[:,np.newaxis,:] * rO[np.newaxis,:,np.newaxis]

				# Put it back in the correct shape
				ret = np.reshape(ret, self.shape + list(other.shape) + sh)

				return ret

			name = '(' + self.name + ' * ' + str(other.shape) +')'
			return ArrayFunc(f, self.shape + list(other.shape), self.dim, name=name)

		else:
			name = '(' + self.name + ' * ' + str(other) +')'
			return ArrayFunc(lambda x: self(x)*other, self.shape, self.dim, name=name)

	def __rmul__(self, other):
		'''
		Overrides right multiplication.

		If other is a number this multiplies the function
		by that number. Otherwise other must be a ArrayFunc,
		in which case the new function is the tensor product
		of self and other along all but the coordinate axes,
		and so has shape self.shape + other.shape.
		'''

		if hasattr(other, 'shape'):
			if self.dim != other.dim:
				raise ValueError

			return other * self
		else:
			return self * other

	def __add__(self, other):
		'''
		Overrides addition.
		'''

		# Check if shapes can be broadcast
		checkBroadcast(self.shape, other.shape)

		name = '(' + self.name + ' + ' + other.name +')'
		return ArrayFunc(lambda x: self(x) + other(x), self.shape, self.dim, name=name)

	def __sub__(self, other):
		'''
		Overrides subtraction.
		'''

		return self + -1*other

	def __pow__(self, p):
		'''
		Overrides the power operation.
		'''

		name = self.name + '**' + str(p)
		return ArrayFunc(lambda x: self(x)**p, self.shape, self.dim, name=name)

	def __getitem__(self, sl):
		'''
		Implements slicing.
		'''

		a = np.zeros(self.shape)
		a = a[sl]
		sh0 = list(a.shape)

		def f(x):
			inflat, sh, n = self.flattenInput(x)
			if type(sl) is not slice and type(sl) is not int:
				g = tuple(list(sl) + [slice(0,n)])
			else:
				g = sl
			res = self(inflat)
			res = res[g]
			res = np.reshape(res, sh0 + sh)
			return res

		name = self.name + '[' + str(sl) + ']'
		return ArrayFunc(f, sh0, self.dim, name=name)

	@property
	def flat(self):
		'''
		Returns a flattened version of this function
		'''

		sh = self.shape
		n = np.prod(sh)

		f = lambda x: self(x).reshape([n] + list(x.shape[1:]))

		name = self.name + '_flat'
		return ArrayFunc(f, [n], self.dim, name=name)

	def concatenate(self, other):
		'''
		Returns a ArrayFunc of shape

		[self.shape[0] + other.shape[0]] + self.shape[1:]

		representing the concatenation of this function with the other.
		self.shape[1:] must equal other.shape[1:].
		'''
		if tuple(self.shape[1:]) != tuple(other.shape[1:]):
			raise ValueError('All but the first axis of a concatenated ArrayFunc must match in shape.')

		if self.dim != other.dim:
			raise ValueError('Both functions being concatenated must have the same dimension.')

		f = lambda x: np.concatenate((self(x), other(x)), axis=0)
		sh = [self.shape[0] + other.shape[0]] + self.shape[1:]
		name = 'concatenation(' + self.name + ',' + other.name + ')'

		return ArrayFunc(f, sh, self.dim, name=name)

	def contract(self, einsumOps):
		'''
		This method accepts as input the specification for
		an einsum operation and returns a ArrayFunc representing
		the effect of that operation on this function.
		'''

		# Figure out shape
		a = np.zeros(self.shape)
		a = np.einsum(einsumOps, a)
		sh = a.shape

		name = self.name + '.contract(' + einsumOps + ')'
		return ArrayFunc(lambda x: np.einsum(einsumOps, self(x)), sh, self.dim, name=name)

	def pairContract(self, ax0, ax1):
		'''
		This method contracts the pair of axes specified by ax0 and ax1.
		'''

		# Figure out shape
		a = np.zeros(self.shape)
		a = np.trace(a, axis1=ax0, axis2=ax1)
		sh = a.shape

		name = self.name + '.pairContract(' + str(ax0) + ',' + str(ax1) + ')'
		return ArrayFunc(lambda x: np.trace(self(x), axis1=ax0, axis2=ax1), sh, self.dim, name=name)


	def swapaxes(self, ax0, ax1):
		'''
		This method returns a new function with the specified axes
		exchanged.
		'''

		sh = list(self.shape)
		sh[ax0], sh[ax1] = sh[ax1], sh[ax0]

		name = self.name + '.swapaxes(' + str(ax0) + ',' + str(ax1) + ')'
		return ArrayFunc(lambda x: np.swapaxes(self(x), ax0, ax1), sh, self.dim, name=name)

	def transpose(self, transOps):
		'''
		This method returns a new function with the specified transposition.
		'''

		# Figure out shape
		a = np.zeros(self.shape)
		a = np.transpose(a, axes=transOps)
		sh = a.shape

		name = self.name + '.transpose(' + str(transOps) + ')'
		return ArrayFunc(lambda x: np.transpose(self(x), axes=transOps), sh, self.dim, name=name)

	def moveaxis(self, source, dest):
		'''
		This method applies the numpy moveaxis function.
		'''
		# Figure out shape
		a = np.zeros(self.shape)
		a = np.moveaxis(a, source, dest)
		sh = a.shape

		name = self.name + '.moveaxis(' + str(source) + ',' + str(dest) + ')'
		return ArrayFunc(lambda x: np.moveaxis(self(x), source, dest), sh, self.dim, name=name)		

	def pad(self, d):
		'''
		Returns a ArrayFunc which is identical to self but with
		the specified index d padded by one with zeros. If d is a
		list then all specified indices are padded.
		'''

		if not hasattr(d, '__iter__'):
			d = [d]

		d = set(d)

		def g(x):
			pad_widths = [(0,0) if i not in d else (0,1) for i in range(self.rank)]
			pad_widths = pad_widths + [(0,0) for _ in range(len(x.shape) - 1)]
			return np.pad(self(x), pad_widths, 'constant', constant_values=0)

		sh = list(self.shape)
		for i in d:
			sh[i] += 1

		name = self.name + '.pad(' + str(d) + ')'
		return ArrayFunc(g, sh, self.dim, name=name)

	def unflatten(self, vals):
		'''
		Accepts as input an array of shape (N, ...) and returns
		an array of shape self.shape + (...). This is done such that

		self.unflatten(self.flat(x)) == self(x)
		'''

		sh = self.shape + list(vals.shape[1:])
		x = np.reshape(vals, sh)
		return x

	def flattenInput(self, x):
		'''
		Accepts as input an array of shape (dim, ...) and returns
		an array of shape (dim, N) along with the shape (...).
		'''
		sh = list(x.shape[1:])
		n = np.product(sh)
		x = np.reshape(x, (self.dim, -1))
		return x, sh, n

	def unflattenInput(self, x, sh):
		'''
		Accepts as input an array of shape (dim, N) and returns an
		array of shape [dim] + sh.
		'''
		return np.reshape(x, [self.dim] + list(sh))

	def unflattenOutput(self, vals, extra, sh):
		'''
		Accepts as input an array of shape self.shape + [N] and returns
		an array of shape self.shape + extra + sh. extra must be the shape
		of any additional indices which have been introduced between the
		function index and the vectorized indices.
		'''
		return np.reshape(vals, self.shape + extra + list(sh))

	def reciprocal(self):
		'''
		Returns the reciprocal of self.
		'''

		f = lambda x: 1./self(x)
		return ArrayFunc(f, self.shape, self.dim, name=self.name + '.reciprocal')
