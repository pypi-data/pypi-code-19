# coding=utf-8
"""

"""


from mimircache import *
import numpy as np
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mimircache.c_LRUProfiler as c_LRUProfiler



import os, sys, time, pickle
sys.path.append("../")
sys.path.append("./")
from mimircache import *
from mimircache.bin.conf import initConf

################################## Global variable and initialization ###################################

TRACE_TYPE = "cloudphysics"

TRACE_DIR, NUM_OF_THREADS = initConf(TRACE_TYPE, trace_format='variable')

N = 9





def get_quantile(dat, time_interval):
    reader = vscsiReader(dat)

    # timestamps = []
    # ts = reader.read_time_request()
    # while ts:
    #     timestamps.append(ts[0])
    #     ts = reader.read_time_request()
    # reader.reset()

    p = LRUProfiler(reader)
    rd = p.get_reuse_distance()
    # assert rd.shape[0] == len(timestamps)

    bp = cHeatmap().getBreakpoints(reader, 'r', time_interval)
    quantiles = []
    for i in range(len(bp) - 1):
        # print(count_quantile(rd[bp[i]: bp[i + 1]]))
        quantiles.append(count_quantile(rd[bp[i]: bp[i + 1]]))

    print(len(quantiles))
    print(quantiles)
    return quantiles


def count_quantile(rd, n=N):
    """

    :param rd:
    :param n:
    :return: each element in l is rd
    """
    rd_sorted = np.sort(rd[rd != -1])
    slice_size = rd_sorted.shape[0] // n
    l = []
    for i in range(n):
        l.append(rd_sorted[slice_size * (i + 1) - 1])
    return l


def RD_quantile(rd, n=-1):
    """

    :param rd:
    :param n:
    :return: l, ith pos in l is the count of RD in this bucket
    """
    maxRD = np.max(rd)
    l = [0] * int(math.log2(maxRD)+1)
    rd = rd[rd != -1]
    rd[rd==0] = 1
    rd_log = np.log2(rd).astype(int)
    for x in rd_log:
        # print(x)
        l[x] += 1
    return l


def rd_regression(dat, time_interval=100000000):
    quantiles = get_quantile(dat, time_interval)
    for i in range(N):
        l = [x[i] for x in quantiles]
        ax= plt.subplot(3, 3, i+1)
        ax.plot(l)
    plt.xlabel("real time")
    plt.ylabel("reuse distance")
    plt.savefig("{}_rd.png".format("all"))
    plt.clf()


if __name__ == "__main__":
    rd_regression('{}/w100_vscsi1.vscsitrace'.format(TRACE_DIR))
