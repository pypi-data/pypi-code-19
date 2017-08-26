import numpy as np

__all__ = ['cmp_vec', 'cmp_flt']

# mathext --> Math Extended for implant library package.


def cmp_vec(v1, v2, tol):
	if (v1 is None and v2 is None) or (np.allclose(v1, v2, 0.0, tol)):
		return True
	return False


def cmp_flt(f1, f2, tol):
	return abs(f1 - f2) < tol
