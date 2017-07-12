import numpy as np
from .arrfunc import ArrayFunc
from .linalg import det, inverse, pinverse

eps = 1e-10

def test_call():
	f = ArrayFunc(lambda x: x[0][np.newaxis], [1], 2)

	z = np.random.randn(2, 10, 3, 2)

	assert tuple(f(z).shape) == tuple([1] + list(z.shape[1:]))
	assert np.sum(np.abs(f(z) - z[0])) == 0

def test_scalar_mul():
	f = ArrayFunc(lambda x: x[0][np.newaxis], [1], 2)

	g = 2*f
	h = f*2

	z = np.random.randn(2, 10, 3, 2)

	assert np.sum(np.abs(g(z) - 2*z[0])) == 0
	assert np.sum(np.abs(h(z) - 2*z[0])) == 0

def test_func_mul():
	f = ArrayFunc(lambda x: x[0][np.newaxis], [1], 2)
	k = ArrayFunc(lambda x: np.array([[x[0],x[1]],[x[0],x[1]]]), [2,2], 2)

	g = k*f
	h = f*k

	z = np.random.randn(2, 10, 3, 2)

	assert tuple(g.shape) == tuple(k.shape + f.shape)
	assert tuple(h.shape) == tuple(f.shape + k.shape)
	assert g(z).shape == tuple(k.shape + f.shape + list(z.shape[1:]))
	assert h(z).shape == tuple(f.shape + k.shape + list(z.shape[1:]))

	assert np.sum((h(z) - f(z)[:,np.newaxis,np.newaxis]*k(z)[np.newaxis,:])**2) == 0
	assert np.sum((g(z) - k(z)[:,:,np.newaxis]*f(z)[np.newaxis,np.newaxis,:])**2) == 0

def test_func_add():
	k = ArrayFunc(lambda x: np.array([[x[0],x[1]],[x[0],x[1]]]), [2,2], 2)
	jk = ArrayFunc(lambda x: 2*np.array([[x[0],x[1]],[x[0],x[1]]]), [2,2], 2)

	z = np.random.randn(2, 10, 2, 4)

	assert np.sum(((jk + k)(z) - 3*k(z))**2) == 0

def test_func_sub():
	k = ArrayFunc(lambda x: np.array([[x[0],x[1]],[x[0],x[1]]]), [2,2], 2)
	jk = ArrayFunc(lambda x: 2*np.array([[x[0],x[1]],[x[0],x[1]]]), [2,2], 2)

	z = np.random.randn(2, 10, 2, 4)

	assert np.sum(((jk - k)(z) - k(z))**2) == 0

def test_func_pow():
	k = ArrayFunc(lambda x: np.array([[x[0],x[1]],[x[0],x[1]]]), [2,2], 2)

	q = k**2

	z = np.random.randn(2, 10, 2, 4)

	assert np.sum((q(z) - k(z)*k(z))**2) == 0

def test_func_basic_slice():
	k = ArrayFunc(lambda x: np.array([[x[0],x[1]],[x[0],x[1]]]), [2,2], 2)

	q = k[0:1]

	z = np.random.randn(2, 10, 2, 4)

	assert np.sum((q(z) - k(z)[0:1])**2) == 0

def test_func_int_slice():
	k = ArrayFunc(lambda x: np.array([[x[0],x[1]],[x[0],x[1]]]), [2,2], 2)

	q = k[0]

	z = np.random.randn(2, 10, 2, 4)

	assert np.sum((q(z) - k(z)[0])**2) == 0

def test_func_adv_slice():
	k = ArrayFunc(lambda x: np.array([[x[0],x[1]],[x[0]**2,x[1]**3]]), [2,2], 2)

	q = k[0,0]
	p = k[...,0]
	m = k[(1,0),:]

	z = np.random.randn(2, 10, 2, 4)

	assert np.sum((q(z) - k(z)[0,0])**2) == 0
	assert np.sum((p(z) - k(z)[:,0])**2) == 0
	assert np.sum((m(z) - k(z)[(1,0),:])**2) == 0

def test_func_flat():
	k = ArrayFunc(lambda x: np.array([[x[0],x[1]],[x[0]**2,x[1]**3]]), [2,2], 2)
	q = k.flat

	z = np.random.randn(2, 10, 2, 4)

	assert np.sum((q(z) - k(z).reshape(4,10,2,4))**2) == 0


def test_func_unflat():
	k = ArrayFunc(lambda x: np.array([[x[0],x[1]],[x[0]**2,x[1]**3]]), [2,2], 2)
	q = k.flat

	z = np.random.randn(2, 10, 2, 4)

	assert np.sum((k.unflattenOutput(q(z), [], z.shape[1:]) - k(z))**2) == 0

def test_func_flatIn():
	k = ArrayFunc(lambda x: np.array([[x[0],x[1]],[x[0]**2,x[1]**3]]), [2,2], 2)

	z = np.random.randn(2, 10, 2, 4)

	assert k.flattenInput(z)[0].shape == (2, 80)

	assert np.sum((k.unflattenInput(*k.flattenInput(z)[:2]) - z)**2) == 0

def test_func_det():
	k = ArrayFunc(lambda x: np.array([[x[0],x[1]],[x[0]**2,x[1]**3]]), [2,2], 2)

	kdet = det(k)

	z = np.random.randn(2, 10, 2, 4)

	assert np.sum((kdet(z) - z[0]*z[1]**3 + z[1]*z[0]**2)**2) < eps

def test_func_pinv():
	k = ArrayFunc(lambda x: np.array([[x[0],x[1]],[x[0]**2,x[1]**3]]), [2,2], 2)

	kdet = det(k)
	kinv = pinverse(k)

	z = np.random.randn(2, 10, 2, 4)

	# Compare against analytic inverse
	assert np.sum((kinv(z) - np.array([[z[1]**3,-z[1]],[-z[0]**2,z[0]]])/kdet(z))**2) < eps


def test_func_inv():
	k = ArrayFunc(lambda x: np.array([[1 + x[0],x[1]],[x[0]**2,1 + 4*x[1]**3]]), [2,2], 2)

	kdet = det(k)
	kinv = inverse(k)

	z = np.random.randn(2, 10, 2, 4)

	i0 = kinv(z)
	i1 = np.array([[1 + 4*z[1]**3,-z[1]],[-z[0]**2,1 + z[0]]])/kdet(z)

	# Compare against analytic inverse
	assert np.sum((i0 - i1)**2) < eps


