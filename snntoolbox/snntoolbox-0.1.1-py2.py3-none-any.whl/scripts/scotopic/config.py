# coding=utf-8

""" Scotopic vision configuration."""

import os
import numpy as np
from collections import OrderedDict

lr = 0.004
num_epochs = 80
# th_array = np.log(np.logspace(np.log10(0.1 + 1e-4), np.log10(1 - 1e-4), 200))
# th_array = np.hstack([th_array[0:195:5], th_array[195:]])
th_array = np.log(np.logspace(np.log10(0.1 + 1e-4), np.log10(1 - 1e-4), 50))
gpu = 0

settings_scotopic = OrderedDict({
    'gpu': gpu,
    'lr': lr,
    'dataset': 'mnist',
    'model_type': 'waldnet-wb1',
    'model_name': 'val_lrx{:.2f}'.format(lr),
    'sp': {'mode': 'batch', 'alpha': 0, 'estimate_ppp': False, 'max_ppp': 220,
           'ppp_array': [.22, 2.2, 22, 220], 'snr': 0.97 / 0.03,
           'test_ppp_array': np.logspace(np.log10(0.22), np.log10(220), 50),
           'amp_sigma': 0, 'fpn_simga': 0, 'jitter': 0, 'dis_th': []},
    'th_array': th_array,
    'validate': True,
    'whiten_data': False,
    'contrast_normalization': False,
    'train': {'gpus': gpu, 'learning_rate': lr * np.ones(num_epochs),
              'num_epochs': num_epochs}
})


def update_settings_scotopic(s):
    """

    :param s: 
    :type s: 
    """

    settings_scotopic.update(s)

    if not os.path.exists(settings_scotopic['data_dir']):
        os.makedirs(settings_scotopic['data_dir'])
