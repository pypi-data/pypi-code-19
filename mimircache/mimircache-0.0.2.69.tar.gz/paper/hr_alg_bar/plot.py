# coding=utf-8



from mimircache import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['ytick.labelsize'] = 16

def load_data():
    all_data = []
    # w94
    data = {'FIFO': 0.11043884,
            # "LFU": 0.01942723,
            'LRU': 0.11209758,
            "AMP": 0.23421291,
            "PG": 0.11481527,
            "Mithril_FIFO": 0.66321772,
            # "Mithril_LFU": 0.036691,
            "Mithril_LRU": 0.66431189,
            "Mithril_AMP": 0.71961534}
    all_data.append(data)

    # prxy1
    data = {'FIFO': 0.4705818,
            # "LFU": 0.57799214,
            'LRU': 0.47083247,
            "AMP": 0.46204835,
            "PG": 0.69391018,
            "Mithril_FIFO": 0.96601522,
            # "Mithril_LFU":0.57937729,
            "Mithril_LRU": 0.96637392,
            "Mithril_AMP": 0.96884716}
    all_data.append(data)

    # w91
    data = {'FIFO': 0.51867533,
            # "LFU": 0.29121304,
            'LRU': 0.52418309,
            "AMP": 0.55876422,
            "PG": 0.56768978,
            "Mithril_FIFO": 0.78601778,
            # "Mithril_LFU": 0.35842627,
            "Mithril_LRU": 0.79129922,
            "Mithril_AMP": 0.80495417}
    all_data.append(data)

    # src1_2
    data = {'FIFO': 0.54608017,
            # "LFU": 0.40399462,
            'LRU': 0.55205888,
            "AMP": 0.57381719,
            "PG": 0.55565101,
            "Mithril_FIFO": 0.79721069,
            # "Mithril_LFU": 0.41178694,
            "Mithril_LRU": 0.80094433,
            "Mithril_AMP": 0.81162751}
    all_data.append(data)

    # w89
    data = {'FIFO': 0.80545294,
            # "LFU": 0.29479805,
            'LRU': 0.80699241,
            "AMP": 0.88509184,
            "PG": 0.81137693,
            "Mithril_FIFO": 0.87123424,
            # "Mithril_LFU": 0.496276,
            "Mithril_LRU": 0.87374085,
            "Mithril_AMP": 0.91181129}
    all_data.append(data)

    # proj_3
    data = {'FIFO': 0.63038903,
            # "LFU": 0.04649468,
            'LRU': 0.63166767,
            "AMP": 0.87964058,
            "PG": 0.63637751,
            "Mithril_FIFO": 0.83350724,
            # "Mithril_LFU": 0.08292584,
            "Mithril_LRU": 0.83419555,
            "Mithril_AMP": 0.91615552}
    all_data.append(data)
    traces = ["w94", "prxy", "w91", "src1", "w89", "proj"]


    return all_data, traces






def plot_bar_all():
    all_data, names = load_data()
    for dat, name in zip(all_data, names):
        plot_bar(dat, name)



def plot_bar(dat, name):
    alg_list = ['FIFO', 'LRU', "AMP", "PG", "Mithril_FIFO", "Mithril_LRU", "Mithril_AMP"]

    ind = np.arange(1, 1 + len(alg_list))
    width = 0.5

    hr = [dat[alg] for alg in alg_list]

    # plt.tight_layout()
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, hr, width, color='b')

    ax.set_ylabel('Hit Ratio', fontsize=20)
    # ax.set_title('Hit Ratio of {}'.format(name))
    # ax.set_xticks(ind + width / 2)
    ax.set_xticklabels([None]+alg_list, rotation=30, fontsize=20)
    # plt.margins(0.2)

    diff = max(hr) - min(hr)
    # if name == 'w89':
    #     ax.yaxis.set_ticks(np.arange(min(hr)-0.1*diff, min(1, max(hr)+0.1*diff), 0.05))
    # else:
    ax.set_ylim([min(hr)-0.1*diff, min(1, max(hr)+0.1*diff)] )
    plt.subplots_adjust(bottom=0.24, left=0.20)

    # women_means = (25, 32, 34, 20, 25)
    # women_std = (3, 5, 2, 3, 3)
    # rects2 = ax.bar(ind + width, women_means, width, color='y', yerr=women_std)

    plt.savefig("{}.png".format(name), dpi=600)
    plt.savefig("{}.eps".format(name))




if __name__ == "__main__":
    plot_bar_all()