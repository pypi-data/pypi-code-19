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
import glob
import os
import shutil
import sqlite3
import tempfile
import threading
import time
import matplotlib.pyplot as plt
import pywt
import numpy as np
import pandas as pd
from scipy.sparse import diags
from sklearn.decomposition import PCA
from sklearn.preprocessing import Binarizer
from sklearn.preprocessing import normalize
from sklearn.preprocessing import RobustScaler
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import scale


def time_domain_conversion(file_name, N, fc, s):
  result = np.loadtxt(file_name)
  pres = result[:, 2] + 1j * result[:, 3]
  df = result[1, 4] - result[0, 4]
  f0 = result[0, 4]
  fN = result[-1, 4]
  freq = np.arange(f0, fN + df, df)
  pre_freq = np.arange(df, f0, df)
  pre_pres = np.zeros_like(pre_freq)
  freq = np.hstack((pre_freq, freq))
  post_freq = np.arange(fN + df, N * df + df, df)
  post_pres = np.zeros_like(post_freq)
  freq = np.hstack((freq, post_freq))
  gaussian_filter = 1 / (s * np.sqrt(2 * np.pi)) * np.exp(
    -(freq - fc) ** 2 / (2 * s ** 2))
  pres = np.hstack((pre_pres, pres, post_pres))
  pres *= gaussian_filter
  signal = np.real(np.fft.ifft(pres, N))
  signal2 = signal
  signal3 = (signal2 - np.mean(signal2)) / np.max(np.abs(signal2))
  signal3 = signal3[::-1]
  return signal3


def new_signal_database(in_path, out_path, N, fc, s):
  db_name = out_path + '/' + in_path.split('/')[-1] + '.sqlite'
  try:
    print('pass')
    os.remove(db_name)
  finally:
    pass
  par_file = open(in_path + '/parameters.csv', 'r')
  parameters = pd.read_csv(par_file)
  par_names = parameters.columns.values.tolist()
  create_table = 'CREATE TABLE signals (id INT '
  for p in parameters:
    create_table += ', ' + p + ' REAL'
  create_table += ', waveform BLOB)'
  db_conn = sqlite3.connect(db_name)
  db_cursor = db_conn.cursor()
  db_cursor.execute(create_table)
  pres_files = sorted(glob.glob(os.path.join(in_path, '*.pres')))
  insert_row = 'INSERT INTO signals VALUES (?'
  insert_row += ', ?' * (len(par_names) + 1)
  insert_row += ')'
  par_np = parameters.as_matrix()
  for i, pf in enumerate(pres_files):
    # signal is stored in bytecode form
    signal = time_domain_conversion(pf, N, fc, s).tostring()
    row_tuple = (i + 1, *tuple(par_np[i]), signal)
    db_cursor.executemany(insert_row, [row_tuple])
  db_conn.commit()
  db_cursor.close()
  db_conn.close()
  par_file.close()


def signal_from_database(db_file, signal_id):
  db_conn = sqlite3.connect(db_file)
  db_cursor = db_conn.cursor()
  select_row = 'SELECT waveform FROM signals WHERE id=?'
  db_cursor.execute(select_row, (signal_id,))
  signal = np.fromstring(db_cursor.fetchone()[0], dtype=np.float64)
  db_cursor.close()
  db_conn.close()
  return signal


def dataset_from_wp2d(wp2d_db):
  db_conn = sqlite3.connect(wp2d_db)
  db_cursor = db_conn.execute('SELECT wp_features FROM dataset')
  fe2d = db_cursor.fetchall()
  dataset_list = []
  for it in fe2d:
    dataset_list.append(np.fromstring(it[0]))
  db_cursor.close()
  db_conn.close()
  dataset = np.array(dataset_list)
  dataset = dataset.reshape(dataset.shape[0], dataset.shape[1]//2, 2)
  print(dataset.shape)
  return dataset


def signal_wpt(signal, wavelet='db4', level=3):
  wp = pywt.WaveletPacket(
    data=signal, wavelet=wavelet, mode='sym', maxlevel=level)
  l_array = wp.get_level(level, order='freq')
  l_list = []
  for it in l_array:
    l_list.append(it.data)
  wpmat = np.array(l_list, dtype=np.float64)
  return wpmat


def signal_greedy_wpt(signal, wavelet='db4', level=3):
  len_signal = signal.shape[0]
  num_s = 2**level
  per_i = int(len_signal/num_s)
  spec = np.zeros((num_s, len_signal))
  for i in range(num_s):
    s_i = np.roll(signal, -i)
    wp_i = signal_wpt(s_i, wavelet=wavelet, level=level)
    for j in range(per_i):
      spec[:, i + j*num_s] = wp_i[:, j]
  return spec


def energy_contribution_by_scale(wpmat, scales):
  mat = wpmat[scales, :]
  matnorm = np.linalg.norm(mat, 2, 0)
  n = matnorm.shape[-1]
  diagonals = [[0.4]*n, [0.2]*(n-1), [0.2]*(n-1), [0.1]*(n-2), [0.1]*(n-2)]
  filt = diags(diagonals, [0, -1, 1, -2, 2]).toarray()
  filt_matnorm = np.dot(filt, matnorm)
  mo2 = sum(filt_matnorm[-11:-1] + filt_matnorm[0:10])/20.0 + 0.1
  binarizer = Binarizer(copy=True, threshold=mo2)
  b = binarizer.transform(filt_matnorm.reshape(-1, 1))
  x = np.where(b)[0]
  a = 0
  b = -1
  while x[a]+1 not in x:
    a += 1
  while x[b]-1 not in x:
    b -= 1
  energy_mat = np.abs(mat[:, range(x[a], x[b]+1)])
  energy_mat_norm = np.linalg.norm(energy_mat, 2, 0)
  energy_contribution = 1.0 * mat[:, range(x[a], x[b]+1)]/energy_mat_norm
  return energy_contribution


def energy_normalization(wpmat, scales=None):
  if scales is None:
    mat = wpmat
  else:
    mat = wpmat[scales, :]
  matnorm = np.linalg.norm(mat, 2, 0)
  n = matnorm.shape[-1]
  diagonals = [[0.4]*n, [0.2]*(n-1), [0.2]*(n-1), [0.1]*(n-2), [0.1]*(n-2)]
  filt = diags(diagonals, [0, -1, 1, -2, 2]).toarray()
  filt_matnorm = np.dot(filt, matnorm)
  mo2 = sum(filt_matnorm[-11:-1] + filt_matnorm[0:10])/20.0 + 0.1
  binarizer = Binarizer(copy=True, threshold=mo2)
  b = binarizer.transform(filt_matnorm.reshape(-1, 1))
  x = np.where(b)[0]
  a = 0
  b = -1
  while x[a]+1 not in x:
    a += 1
  while x[b]-1 not in x:
    b -= 1
  energy_mat_norm = np.linalg.norm(mat[:, range(x[a], x[b]+1)], 1, 0)
  energy_mat_norm = energy_mat_norm/ np.max(energy_mat_norm)
  energy_contribution = mat[:, range(x[a], x[b]+1)]/energy_mat_norm
  energy_contribution = np.concatenate(
    (energy_contribution, np.expand_dims(energy_mat_norm, 0)), axis=0)
  return energy_contribution


def crop_wp(wpmat, scales=None):
  if scales is None:
    mat = wpmat
  else:
    mat = wpmat[scales, :]
  matnorm = np.linalg.norm(mat, 2, 0)
  n = matnorm.shape[-1]
  diagonals = [[0.4]*n, [0.2]*(n-1), [0.2]*(n-1), [0.1]*(n-2), [0.1]*(n-2)]
  filt = diags(diagonals, [0, -1, 1, -2, 2]).toarray()
  filt_matnorm = np.dot(filt, matnorm)
  mo2 = sum(filt_matnorm[0:20])/20.0 + 0.25
  binarizer = Binarizer(copy=True, threshold=mo2)
  b = binarizer.transform(filt_matnorm.reshape(-1, 1))
  x = np.where(b)[0]
  a = 0
  b = -1
  while x[a]+1 not in x:
    a += 1
  while x[b]-1 not in x:
    b -= 1
  crop_mat = mat[:, range(x[a], x[b]+1)]
  return crop_mat


def cumsum_scalling(signal):
  cum_scaller = np.cumsum(np.abs(signal), axis=0)
  cum_scaller = cum_scaller/np.expand_dims(cum_scaller[-1], -1)
  return signal * cum_scaller


def agwn(signal, snr=10):
  signal_sqrt_energy = np.linalg.norm(signal)
  sigma = signal_sqrt_energy*10**(-snr/20)/np.sqrt(len(signal))
  noise = np.random.normal(0, sigma, len(signal))
  signal = signal + noise
  return signal


def blurring_pentad(signal, elements):
  sig_len = len(signal)
  print(sig_len)
  diagonals = [[elements[0]]*sig_len,
               [elements[1]]*(sig_len-1),
               [elements[1]]*(sig_len-1),
               [elements[2]]*(sig_len-2),
               [elements[2]]*(sig_len-2)]
  blurring_mat = diags(diagonals, [0, -1, 1, -2, 2]).toarray()
  blurring_sig = np.dot(blurring_mat, signal)
  return (blurring_sig - np.mean(blurring_sig)) / np.max(np.abs(blurring_sig))


def db_to_csv(database, csv_filename, ids):
  signals = []
  for id in ids:
    signal = signal_from_database(database, id)
    signals.append(signal)
  signals = np.array(signals)
  np.savetxt(csv_filename, signals, delimiter=',')


def sdiff_penalty(n1, n2, kappa):
  c = np.exp(kappa*np.abs(n1-n2)/n1)
  return c


def program_exec(program='mode1_arg',
                 template='data',
                 tfunc=None,
                 values=None,
                 N=1024,
                 cfreq=100,
                 bandwidth=50,
                 tmpdir='/tmp',
                 nodes={'localhost': 4},
                 id=0):
  tic = time.time()
  tmpd = tempfile.mkdtemp(dir=tmpdir)
  cores_per_node = list(nodes.values())
  hostnames = list(nodes.keys())
  cum_cores = np.cumsum(cores_per_node)
  num_cores = cum_cores[-1]
  if values is None:
    values_shape = [1]
  else:
    values_shape = values.shape
  exec_bank = {}
  mode1_arg = program
  for host in hostnames:
    exec_bank[host] = [mode1_arg + ' :::']
  for i in range(values_shape[0]):
    mod = i % num_cores
    # find the id of the node
    n = next(x[0] for x in enumerate(cum_cores) if x[1] > mod)
    file_number = str(i).zfill(5)
    c = 'run_' + file_number
    exec_bank[hostnames[n]].append(c)
    run_i = open(tmpd + '/' + c, 'w')
    if tfunc is None:
      run_i.write(template)
    else:
      run_i.write(template % tfunc(values[i, :]))
    run_i.close()
  processes = []
  for n, host in enumerate(hostnames):
    mode1_exec = str.join(' ', exec_bank[host])
    com = 'ssh ' + host + ' \' cd ' + tmpd + ' ; parallel -j' \
          + str(cores_per_node[n]) + ' nohup ' + mode1_exec + \
          ' ::: > /dev/null 2>&1 \' '
    processes.append(threading.Thread(target=node_os_system, args=(com,)))
  for p in processes:
    p.start()
  for p in processes:
    p.join()
  toc = time.time()
  signals = []
  for i in range(values_shape[0]):
    file_number = str(i).zfill(5)
    c = tmpd + '/run_' + file_number + '.pres'
    signals.append(time_domain_conversion(c, N, cfreq, bandwidth))
  shutil.rmtree(tmpd)
  print(values_shape[0], 'signals were calculated in', toc-tic, 'sec')
  return np.array(signals)


# run a script with arguments using multiple cores from various machines
def program_run(program,
                template,
                tfunc=None,
                values=None,
                tmpdir='/tmp',
                nodes={'localhost': 4}):
  tmpd = tempfile.mkdtemp(dir=tmpdir)
  cores_per_node = list(nodes.values())
  hostnames = list(nodes.keys())
  cum_cores = np.cumsum(cores_per_node)
  num_cores = cum_cores[-1]
  if values is None:
    values_shape = [1]
  else:
    values_shape = values.shape
  exec_bank = {}
  mode1_arg = program
  for host in hostnames:
    exec_bank[host] = [mode1_arg + ' :::']
  for i in range(values_shape[0]):
    mod = i % num_cores
    # find the id of the node
    n = next(x[0] for x in enumerate(cum_cores) if x[1] > mod)
    file_number = str(i).zfill(5)
    c = 'run_' + file_number
    exec_bank[hostnames[n]].append(c)
    run_i = open(tmpd + '/' + c, 'w')
    if tfunc is None:
      run_i.write(template)
    else:
      run_i.write(template % tfunc(values[i, :]))
    run_i.close()
  processes = []
  for n, host in enumerate(hostnames):
    mode1_exec = str.join(' ', exec_bank[host])
    com = 'ssh ' + host + ' \' cd ' + tmpd + ' ; parallel -j' \
          + str(cores_per_node[n]) + ' nohup ' + mode1_exec + \
          ' ::: > /dev/null 2>&1 \' '
    processes.append(threading.Thread(target=node_os_system, args=(com,)))
  for p in processes:
    p.start()
  for p in processes:
    p.join()


def node_os_system(com):
  os.system(com)
