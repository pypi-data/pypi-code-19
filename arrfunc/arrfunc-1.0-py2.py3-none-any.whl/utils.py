import numpy as np

def checkBroadcast(sh1, sh2):
	'''
	Checks if the specified shapes can be broadcast together
	and emits an error message if they cannot.
	'''

	x = np.zeros(sh1)
	y = np.zeros(sh2)
	try:
		c = np.broadcast(x, y)
	except ValueError:
		print('Error: Shapes not compatible.')
		exit()

def levicivita3D():
	'''
	Returns the full rank-3 levi-civita pseudotensor in three dimensions.
	'''
	ret = np.zeros((3,3,3))
	ret[0,1,2] = 1
	ret[1,2,0] = 1
	ret[2,0,1] = 1
	ret[2,1,0] = -1
	ret[0,2,1] = -1
	ret[1,0,2] = -1

	return ret

def tiledIdentity(z, dim=3):
	'''
	Returns the identity which acts on an array of vectors of shape (dim, ...).
	'''
	ret = np.zeros([dim,dim] + list(z.shape[1:]), dtype=z.dtype)
	for i in range(dim):
		ret[i,i] = 1
	return ret

def reverser(arr, func):
	'''
	This method takes as input an array of shape (N, N, ...) and a function
	which expects the array to have shape (..., N, N), and applies the function
	to the array by performing the appropriate transpose operations.
	'''
	arr = np.transpose(arr)
	arr = np.swapaxes(arr, -1, -2)
	arr = func(arr)
	arr = np.transpose(arr)
	arr = np.swapaxes(arr, 0, 1)
	return arr

def multiplyList(items):
	'''
	Returns the ordered product of the given items.
	'''
	f = items[0]
	for g in items[1:]:
		f = f * g
	return f