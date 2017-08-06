# coding=utf-8
"""
this file plots the hit of orginal data, LRU, Mithril similar to the one mentioned by Avani
"""

import pickle
import matplotlib
matplotlib.use("agg")
from matplotlib import pyplot as plt
from mimircache import *
from collections import defaultdict



from init_confs import init
TRACE_TYPE = "cloudphysics"
TRACE_DIR, NUM_OF_THREADS = init(traceType=TRACE_TYPE)


DEFAULT_PARAM = {"max_support": 4,
                 "min_support": 1,
                 "confidence": 0,
                 "item_set_size": 20,
                 "prefetch_list_size": 2,
                 "cache_type": "LRU",
                 "sequential_type": 0,
                 "max_metadata_size": 0.1,
                 "block_size": 64 * 1024,
                 "sequential_K": 0,
                 "cycle_time": 2,
                 "AMP_pthreshold": 256
                }


def runMithril(dat):
    c = cachecow()
    c.open(dat, data_type='l')
    nu = c.reader.get_num_unique_req()
    p = c.profiler("mimir", cache_params=DEFAULT_PARAM, cache_size=int(nu/100), bin_size=int(nu/100))
    print(p.get_hit_rate())

def runLRU(dat):
    c = cachecow()
    c.open(dat, data_type='l')
    nu = c.reader.get_num_unique_req()
    p = cGeneralProfiler(c.reader, "LRU", cache_size=int(nu/100), bin_size=int(nu/100))
    print(p.get_hit_rate())



def count_original_data(dat):
    """
    this function count the frequency of blocks in original data
    and return two dict (LBA->freq, LBA->new LBA) # and a list of LBA sorted by freq
    :param dat:
    :return:
    """
    c = cachecow()
    c.open(dat)
    d = defaultdict(int)
    d2 = {}
    for k in c:
        d[int(k)] += 1
    sorted_list = sorted(d.items(), key=lambda i:i[1], reverse=True)

    counter = 0
    for t in sorted_list:
        d2[t[0]] = counter
        counter += 1

    return d, d2

def load_hit(dat):
    d = defaultdict(int)
    with open(dat, 'r') as ifile:
        for line in ifile:
            d[int(line.strip())-1] += 1
    return d


def plot(d_ori, d_LRU, d_Mithril, d_mapping):
    l_ori = [0] * len(d_ori)
    l_LRU = [0] * len(d_ori)
    l_Mithril = [0] * len(d_ori)
    l = [i for i in range(len(d_ori))]

    for k, v in d_ori.items():
        l_ori[d_mapping[k]] = v
    for k, v in d_LRU.items():
        try:
            l_LRU[d_mapping[k]] = v
        except:
            print("key not found {}, value {}".format(str(k), str(v)))
            sys.exit(1)
    for k, v in d_Mithril.items():
        l_Mithril[d_mapping[k]] = v


    plt.gca().tick_params(axis='both', which='major', labelsize=24)
    plt.gca().tick_params(axis='both', which='minor', labelsize=24)

    plt.plot(l, l_ori, "r.", label="original", alpha=0.25)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel("LBA sorted by frequency", fontsize=30)
    plt.ylabel("hit count", fontsize=30)
    plt.savefig("hit_ori.png", bbox_inches='tight', pad_inches=0.28, dpi=600)
    plt.clf()


    plt.gca().tick_params(axis='both', which='major', labelsize=24)
    plt.gca().tick_params(axis='both', which='minor', labelsize=24)

    plt.plot(l, l_LRU, "g.", label="LRU", alpha=0.25)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel("LBA sorted by frequency", fontsize=30)
    plt.ylabel("hit count", fontsize=30)
    plt.savefig("hit_LRU.png", bbox_inches='tight', pad_inches=0.28, dpi=600)
    plt.clf()

    plt.gca().tick_params(axis='both', which='major', labelsize=24)
    plt.gca().tick_params(axis='both', which='minor', labelsize=24)

    plt.plot(l, l_Mithril, "b.", label="Mithril", alpha=0.25)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel("LBA sorted by frequency", fontsize=30)
    plt.ylabel("hit count", fontsize=30)
    plt.savefig("hit_Mithril.png", bbox_inches='tight', pad_inches=0.28, dpi=600)
    plt.clf()

    # calculate for CCDF
    # for i in range(len(l_ori)-2, 0, -1):
    #     l_ori[i] += l_ori[i+1]
    #     l_LRU[i] += l_LRU[i+1]
    #     l_Mithril[i] += l_Mithril[i+1]


    # plt.plot(l, l_ori, "r.", label="original") #, alpha=0.3)
    # plt.plot(l, l_LRU, "g.", label="LRU") #, alpha=0.3)
    # plt.plot(l, l_Mithril, "b.", label="Mithril") # , alpha=0.3)
    # plt.xscale('log')
    # plt.yscale('log')
    # plt.xlabel("LBA(sorted by frequency in original trace)")
    # plt.ylabel("hit count")
    # plt.legend(loc="upper left")
    # plt.savefig("hit.png", dpi=600)
    # plt.clf()



    # calculate for differecne between Mithril and LRU
    # d_diff = dict(d_Mithril)
    # l_diff = [0] * len(d_ori)
    # for k, v in d_LRU.items():
    #     if k in d_diff:
    #         d_diff[k] -= v
    # for k, v in d_diff.items():
    #     l_diff[d_mapping[k]] = v
    #
    # plt.plot(l, l_diff, "b.", label="difference") # , alpha=0.3)
    # plt.xscale('log')
    # # plt.yscale('log')
    # plt.xlabel("LBA(sorted by frequency in original trace)")
    # plt.ylabel("hit count")
    # plt.legend(loc="upper left")
    # plt.savefig("hit_diff.png", dpi=600)
    # plt.clf()









if __name__ == "__main__":
    import time
    t0 = time.time()

    ####################### generate data ########################
    # runMithril("{}/{}".format(TRACE_DIR, "w94.txt"))
    # runLRU("{}/{}".format(TRACE_DIR, "w94.txt"))

    ##################### prepare plotting #######################
    d_ori, d_mapping = count_original_data("{}/{}".format(TRACE_DIR, "w94.txt"))
    d_LRU = load_hit("w94.LRU.hit")
    d_Mithril = load_hit("w94.M.hit")

    with open("temp.pickle", 'wb') as ofile:
        pickle.dump((d_ori, d_LRU, d_Mithril, d_mapping), ofile)

    # with open("temp.pickle", 'rb') as ifile:
    #     d_ori, d_LRU, d_Mithril, d_mapping = pickle.load(ifile)


    print("key size: {}: {}: {}".format(len(d_ori), len(d_LRU), len(d_Mithril)))

    plot(d_ori, d_LRU, d_Mithril, d_mapping)

    print(time.time() - t0)

