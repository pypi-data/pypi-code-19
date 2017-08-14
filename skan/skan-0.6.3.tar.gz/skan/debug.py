import numpy as np
from skan import csr

skel = np.array([[]])

skel = np.array([[0, 0, 1, 0, 0],
                 [0, 0, 1, 0, 0],
                 [1, 1, 1, 1, 1]])

g, idxs, deg = csr.skeleton_to_csgraph(skel)
