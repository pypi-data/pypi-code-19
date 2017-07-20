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

import os
import tarfile
import tempfile
import kesmarag.ml
import tensorflow as tf


def hmm_load(path):
  with tarfile.open(path) as tar:
    tar.extractall('/')
    tmp_dir = '/' + tar.getnames()[0]
  with open(tmp_dir + '/hmm_init_params') as hmm_init_params:
    num_states = int(hmm_init_params.readline())
    data_dim = int(hmm_init_params.readline())
  model = megaptera.HiddenMarkovModel(num_states, data_dim)
  model._dir = tmp_dir
  model._epoch = hmm_last_checkpoint(model)
  return model


def hmm_save(hmm, path):
  """Save a HiddenMarkovModel object

  Args:
    hmm: A HiddenMarkovModel object
    path: Path of a .tar.gz file to be saved

  """
  tmp_dir = hmm._dir
  with open(tmp_dir + '/hmm_init_params', 'w') as hmm_init_params:
    hmm_init_params.write(str(hmm._num_states) + '\n')
    hmm_init_params.write(str(hmm._data_dim))
  with tarfile.open(path, 'w') as tar:
    tar.add(tmp_dir)


def hmm_from_known_parameters(p0, tp, mu, sigma):
  # todo
  pass


def hmm_last_checkpoint(hmm):
  """Detects the last checkpoint of the model.

  Args:
    hmm: A HiddenMarkovModel object.

  Returns:
    The number declares the last checkpoint.

  """
  cp_file = open(hmm._dir+'/checkpoint', 'r')
  fl = cp_file.readline()
  lcp = fl.split(':')[1].split('-')[-1][:-2]
  cp_file.close()
  return int(lcp)


def hmm_symkld(hmm1, hmm2, num_samples=10000, num_runs=1):
  """Calculates an estimation of the symmetric kld between
     two HiddenMarkovModel objects

  Args:
    hmm1: The first HiddenMarkovModel object.
    hmm2: The second HiddenMarkovModel object.
    num_samples: Number of the samples for the simulated data.
    num_runs: Number of realizations. For the final estimation mean values
      is considered.

  Returns:
    The estimated symmetric kld

  """
  total_kld = 0.0
  for i in range(num_runs):
    data1, _ = hmm1.generate(num_samples)
    data2, _ = hmm2.generate(num_samples)
    kld = 0.5 * (hmm1.posterior(data1) + hmm2.posterior(data2) /
                 - hmm1.posterior(data2) - hmm2.posterior(data1))/num_samples
    total_kld += kld
  return total_kld/num_runs


def hmm_kld(hmm1, hmm2, num_samples=10000, num_runs=1):
  """Calculates an estimation of the kld between
     two HiddenMarkovModel objects

  Args:
    hmm1: The first HiddenMarkovModel object.
    hmm2: The second HiddenMarkovModel object.
    num_samples: Number of the samples for the simulated data.
    num_runs: Number of realizations. For the final estimation mean values
      is considered.

  Returns:
    The estimated symmetric kld

  """
  total_kld = 0.0
  for i in range(num_runs):
    data1, _ = hmm1.generate(num_samples)
    kld = (hmm1.posterior(data1) - hmm2.posterior(data1))/num_samples
    total_kld += kld
  return total_kld/num_runs


def hmm_kld2(hmm1, hmm2, data):
  kld = (hmm1.posterior(data) - hmm2.posterior(data))/10000
  return kld


def hmm_kld_batch(post1, hmm2, samples):
  pass
