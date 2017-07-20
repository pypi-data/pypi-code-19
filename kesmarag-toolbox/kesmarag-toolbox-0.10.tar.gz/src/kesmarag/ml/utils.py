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
from sklearn.cluster import KMeans


def get_centroids(data, num_centroids):
  r = len(data.shape)
  if r == 3:
    _data = np.concatenate(data, axis=0)
  else:
    assert r == 2
    _data = data
  kmeans = KMeans(n_clusters=num_centroids, random_state=0).fit(_data)
  return kmeans.cluster_centers_


def is_pos_def(mat):
  return np.all(np.linalg.eigvals(mat) > 0)
