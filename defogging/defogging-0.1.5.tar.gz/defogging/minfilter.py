from numpy import *
import utils


def cal_minfilter(src, r):
    """

    :param src: input(one channel only)
    :param r: window radius
    :return: dst
    """
    (hei, wid) = src.shape[0:2]
    dst = zeros((hei, wid))
    src_pad = utils.cal_padding(src, r)
    for i in range(hei):
        for j in range(wid):
            dst[i, j] = amin(src_pad[i:i+2*r+1, j:j+2*r+1])
    return dst
