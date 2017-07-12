import numpy as np
from .utils import reverser
from .arrfunc import ArrayFunc

def vectorPinv(arr):
	'''
	Implements the pseudoinverse of an array of square matrices of shape (..., M, M),
	vectorised over all but the final two indices of arr.
	'''
	res = np.zeros(arr.shape, dtype=arr.dtype)
	for ind, _ in np.ndenumerate(arr[...,0,0]):
		res[ind] = np.linalg.pinv(arr[ind])
	return res

def inverse(f):
	'''
	Returns the inverse of the ArrayFunc f of shape (N,N).
	'''

	if f.rank != 2 or f.shape[0] != f.shape[1]:
		raise ValueError

	name = f.name + '.inverse'
	return ArrayFunc(lambda x: reverser(f(x), np.linalg.inv), f.shape, f.dim, name=name)

def pinverse(f):
	'''
	Returns the pseudoinverse of the ArrayFunc f of shape (N,N).
	'''

	if f.rank != 2 or f.shape[0] != f.shape[1]:
		raise ValueError

	name = f.name + '.pseudoinverse'
	return ArrayFunc(lambda x: reverser(f(x), vectorPinv), f.shape, f.dim, name=name)

def det(f):
	'''
	Returns the determinant of the ArrayFunc f of shape (N,N).
	'''

	if f.rank != 2 or f.shape[0] != f.shape[1]:
		raise ValueError

	def g(x):
		r = f(x)
		r = np.transpose(r)
		r = np.swapaxes(r, -1, -2)
		r = np.linalg.det(r)
		r = np.transpose(r)
		return r[np.newaxis]

	name = f.name + '.det'
	return ArrayFunc(g, [1], f.dim, name=name)