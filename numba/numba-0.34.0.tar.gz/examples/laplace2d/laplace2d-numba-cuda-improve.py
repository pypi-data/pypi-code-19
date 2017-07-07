#!/usr/bin/env python

'''
Speed on OS X 10.8 650M 1024GB GPU: 186s
'''
from __future__ import print_function

import time

import numpy as np

from numba import cuda, f8


# NOTE: CUDA kernel does not return any value

tpb = 16

@cuda.jit(device=True, inline=True)
def get_max(a, b):
    if a > b : return a
    else: return b

@cuda.jit("(f8[:,:], f8[:,:], f8[:,:])")
def jacobi_relax_core(A, Anew, error):
    err_sm = cuda.shared.array((tpb, tpb), dtype=f8)

    ty = cuda.threadIdx.x
    tx = cuda.threadIdx.y
    bx = cuda.blockIdx.x
    by = cuda.blockIdx.y

    n = A.shape[0]
    m = A.shape[1]

    i, j = cuda.grid(2)

    err_sm[ty, tx] = 0
    if j >= 1 and j < n - 1 and i >= 1 and i < m - 1:
        Anew[j, i] = 0.25 * ( A[j, i + 1] + A[j, i - 1] \
                            + A[j - 1, i] + A[j + 1, i])
        err_sm[ty, tx] = Anew[j, i] - A[j, i]

    cuda.syncthreads()

    # max-reduce err_sm vertically
    t = tpb // 2
    while t > 0:
        if ty < t:
            err_sm[ty, tx] = get_max(err_sm[ty, tx], err_sm[ty + t, tx])
        t //= 2
        cuda.syncthreads()

    # max-reduce err_sm horizontally
    t = tpb // 2
    while t > 0:
        if tx < t and ty == 0:
            err_sm[ty, tx] = get_max(err_sm[ty, tx], err_sm[ty, tx + t])
        t //= 2
        cuda.syncthreads()


    if tx == 0 and ty == 0:
        error[by, bx] = err_sm[0, 0]

def main():
    NN = 512
    NM = 512

    A = np.zeros((NN, NM), dtype=np.float64)
    Anew = np.zeros((NN, NM), dtype=np.float64)

    n = NN
    m = NM
    iter_max = 1000

    tol = 1.0e-6
    error = 1.0

    for j in range(n):
        A[j, 0] = 1.0
        Anew[j, 0] = 1.0

    print("Jacobi relaxation Calculation: %d x %d mesh" % (n, m))

    timer = time.time()
    iter = 0

    blockdim = (tpb, tpb)
    griddim = (NN//blockdim[0], NM//blockdim[1])

    error_grid = np.zeros(griddim)

    stream = cuda.stream()

    dA = cuda.to_device(A, stream)          # to device and don't come back
    dAnew = cuda.to_device(Anew, stream)    # to device and don't come back
    derror_grid = cuda.to_device(error_grid, stream)

    while error > tol and iter < iter_max:
        assert error_grid.dtype == np.float64

        jacobi_relax_core[griddim, blockdim, stream](dA, dAnew, derror_grid)

        derror_grid.to_host(stream)


        # error_grid is available on host
        stream.synchronize()

        error = np.abs(error_grid).max()

        # swap dA and dAnew
        tmp = dA
        dA = dAnew
        dAnew = tmp

        if iter % 100 == 0:
            print("%5d, %0.6f (elapsed: %f s)" % (iter, error, time.time()-timer))

        iter += 1

    runtime = time.time() - timer
    print(" total: %f s" % runtime)

if __name__ == '__main__':
    main()
