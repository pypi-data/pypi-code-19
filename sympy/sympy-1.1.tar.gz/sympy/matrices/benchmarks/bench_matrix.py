from __future__ import print_function, division

from sympy import eye, zeros, Integer

i3 = Integer(3)
M = eye(100)


def timeit_Matrix__getitem_ii():
    M[3, 3]


def timeit_Matrix__getitem_II():
    M[i3, i3]


def timeit_Matrix__getslice():
    M[:, :]


def timeit_Matrix_zeronm():
    zeros(100, 100)
