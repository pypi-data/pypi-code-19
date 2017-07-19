# !usr/bin/env python
# coding=gbk
import os
from subprocess import call

import matplotlib.pyplot as plt
import numpy as np
import pip
import scipy.io
import soundfile
from sklearn import preprocessing

INFO = "author:ZHANG Xu-long\nemail:fudan0027zxl@gmail.com\nblog:zhangxulong.site\n"

SEP = os.sep
EPSILON = 1e-8


def voteMaxTimeList(vote_list=[1, 2, 3, 3]):
    vote_list = list(vote_list)
    maxTime = max(vote_list, key=vote_list.count)
    return maxTime


def init_data_dir():
    currentPath = os.getcwd()
    projectName = currentPath.split(SEP)[-1]
    if_no_create_it('../data/' + projectName + '/')
    return '../data/' + projectName + '/'


def savefig(filename, figlist, log=True):
    h = 10
    n = len(figlist)
    # peek into instances
    f = figlist[0]
    if len(f.shape) == 1:
        plt.figure()
        for i, f in enumerate(figlist):
            plt.subplot(n, 1, i + 1)
            if len(f.shape) == 1:
                plt.plot(f)
                plt.xlim([0, len(f)])
    elif len(f.shape) == 2:
        Nsmp, dim = figlist[0].shape
        figsize = (h * float(Nsmp) / dim, len(figlist) * h)
        plt.figure(figsize=figsize)
        for i, f in enumerate(figlist):
            plt.subplot(n, 1, i + 1)
            if log:
                plt.imshow(np.log(f.T + EPSILON))
            else:
                plt.imshow(f.T + EPSILON)
    else:
        raise ValueError('Input dimension must < 3.')
    plt.savefig(filename)


def wavread(filename):
    x, fs = soundfile.read(filename)
    return x, fs


def wavwrite(filename, y, fs):
    soundfile.write(filename, y, fs)
    return 0


def print_to_check(print_list=['a', 'b']):
    for print_item in print_list:
        print(print_item)


def if_no_create_it(file_path):
    the_dir = os.path.dirname(file_path)
    if os.path.isdir(the_dir):
        pass
    else:
        os.makedirs(the_dir)


def del_the_file(file_path):
    os.remove(file_path)


def update_pip_install_packages():
    for dist in pip.get_installed_distributions():
        call("sudo pip install --upgrade " + dist.project_name, shell=True)
    return 0


def align_two_list_with_same_len(list_ref, list_tobe_modify):
    len_ref = len(list_ref)
    len_tobe_modify = len(list_tobe_modify)
    x_ref = range(len_ref)
    x_ref = [x_ref_item / (len_ref / 1.0 / len_tobe_modify) for x_ref_item in x_ref]
    x_tobe_modify = range(len_tobe_modify)
    target_y = np.interp(x_ref, x_tobe_modify, list_tobe_modify)

    return target_y


def read_mat_data(mat_file='file.mat', key='combine_feature'):
    mat = scipy.io.loadmat(mat_file)
    value = mat[key]
    # print numpy.shape(value)
    # print len(value[:,1])
    return value


def save_mat_data(mat_file='file.mat', key='combine_feature', value=''):
    mat = {key: value}
    # print mat
    # print mat_file
    if_no_create_it(mat_file)
    scipy.io.savemat(mat_file, mat)
    return 0


def normalize_data(data, method='min_max', scaler='none'):
    if method == 'min_max':
        if scaler == 'none':
            scaler = preprocessing.MinMaxScaler().fit(data)
        data = scaler.fit_transform(data)
    if method == 'mean_std':
        if scaler == 'none':
            scaler = preprocessing.StandardScaler().fit(data)
        data = scaler.fit_transform(data)

    return data, scaler


def reduceListFilter(tobeReduce=[2, 2, 1, 2, 2, 3, 3, 2, 2, 1, 8]):
    final = []
    count = 0
    tobeReduce = ['start'] + tobeReduce + ['end']
    # print tobeReduce
    for item in tobeReduce:
        if count != len(tobeReduce) - 1 and count != 0:
            if item == tobeReduce[count - 1] and item == tobeReduce[count + 1]:
                final.append(item)
        count += 1

    return final
