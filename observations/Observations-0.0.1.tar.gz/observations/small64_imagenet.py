from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import os

from observations.util import maybe_download_and_extract
from scipy.misc import imread


def small64_imagenet(path):
  """Load the small 64x64 ImageNet data set (van den Oord et al.,
  2016). It consists of millions of 64x64 RGB images.
  """
  path = os.path.expanduser(path)
  url = 'http://image-net.org/small/'
  train = 'train_64x64'
  valid = 'valid_64x64'
  maybe_download_and_extract(path, url + train + '.tar')
  maybe_download_and_extract(path, url + valid + '.tar')

  npz_file = os.path.join(path, 'imgnet_64x64.npz')
  if not os.path.exists(npz_file):
    # Preprocess data and store into npz_file.
    trainx = []
    train_dir = os.path.join(path, train)
    for f in os.listdir(train_dir):
      if f.endswith('.png'):
        print('reading', f)
        filepath = os.path.join(train_dir, f)
        trainx.append(imread(filepath).reshape((1, 64, 64, 3)))

    trainx = np.concatenate(trainx, axis=0)

    testx = []
    test_dir = os.path.join(path, valid)
    for f in os.listdir(test_dir):
      if f.endswith('.png'):
        print('reading', f)
        filepath = os.path.join(test_dir, f)
        testx.append(imread(filepath).reshape((1, 64, 64, 3)))

    testx = np.concatenate(testx, axis=0)
    np.savez(npz_file, trainx=trainx, testx=testx)

  imagenet_data = np.load(npz_file)
  x_train = imagenet_data['trainx']
  x_test = imagenet_data['testx']
  return x_train, x_test
