# -*- coding: utf-8 -*-

from __future__ import print_function

from time import time

import numpy as np
import scipy.linalg
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize


n_samples = 20000
n_lsi = 150

np.random.seed(999999)

X = np.random.randn(n_samples, n_lsi)
normalize(X, norm='l2', copy=False)

print('Test set: {} docs, {} LSI dim'.format(n_samples, n_lsi))

for N_train in [1000, 2000]:
    mod = NearestNeighbors(n_neighbors=1, # always at 1 in FreeDiscovery
                          algorithm='ball_tree',
                          radius=1.0,
                          leaf_size=30,
                          n_jobs=1 # value of 1 best for the benchmark
                          )

    t0 = time()
    mod.fit(X[:N_train, :])
    t1 = time()
    mod.kneighbors(X, return_distance=True)
    t2 = time()

    print('Training set {} docs, t_train= {:.2f} s, t_test = {:.2f}s'.format(
                        N_train, t1-t0, t2-t1))

