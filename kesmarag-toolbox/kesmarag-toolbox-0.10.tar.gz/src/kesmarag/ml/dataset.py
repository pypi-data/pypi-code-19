# Author : Costas Smaragdakis (kesmarag@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

import numpy as np


class DataSet(object):
  def __init__(self, data, labels=None, standardize=True):
    self._data = self._auto_expand(data)
    self._num_examples = self._data.shape[0]
    self._labels = labels
    if labels is not None:
      assert self._num_examples == labels.shape[0]
    self._index_in_epoch = 0
    # Shuffle the data
    perm = np.arange(self._num_examples)
    np.random.shuffle(perm)
    self._data = self._data[perm]
    if labels is not None:
      self._labels = self._labels[perm]

  @property
  def num_examples(self):
    return self._num_examples

  @property
  def data(self):
    return self._data

  @property
  def labels(self):
    return self._labels

  def get_batch(self, batch_size):
    start = self._index_in_epoch
    self._index_in_epoch += batch_size
    if self._index_in_epoch > self._num_examples:
      # Shuffle the data
      perm = np.arange(self._num_examples)
      np.random.shuffle(perm)
      self._data = self._data[perm]
      if self._labels is not None:
        self._labels = self._labels[perm]
      # Start next epoch
      start = 0
      self._index_in_epoch = batch_size
      assert batch_size <= self._num_examples
    end = self._index_in_epoch
    if self._labels is None:
      return self._data[start:end]
    else:
      return self._data[start:end], self._labels[start:end]

  def _auto_expand(self, data):
    r = len(data.shape)
    if r == 2:
      expanded_data = np.expand_dims(data, axis=0)
      return expanded_data
    elif r < 2 or r > 3:
      print('Inappropriate data rank.')
      exit(1)
    else:
      return data
