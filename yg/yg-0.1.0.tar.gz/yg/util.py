# 2017.05.10
# author: yg <gyang274@gmail.com>


import datetime
import glob
import itertools
import json
import os
import sys
import uuid


class yg_timeit(object):
  def __init__(self, f):
    self.f = f

  def __call__(self, *args, **kwargs):
    sys.stdout.write(
      '{}: init at {}.\n'.format(
        self.f.__name__, datetime.datetime.now()
      )
    )
    sys.stdout.flush()

    _ptc = datetime.datetime.now()

    v = self.f(*args, **kwargs)

    _ptd = datetime.datetime.now() - _ptc

    sys.stdout.write(
      '{}: done at {}, used {}.\n'.format(
        self.f.__name__, datetime.datetime.now(), _ptd
      )
    )
    sys.stdout.flush()

    return v


def split_dict_and_write_into_json(adict, path_prefix, filename_prefix, split_into_n_each_file=1024):
  sys.stdout.write('Remove old files.\n')
  sys.stdout.flush()

  for fn in glob.glob(os.path.join(path_prefix, filename_prefix + '*.json')):
    sys.stdout.write('Removing file: {}.\n'.format(fn))
    sys.stdout.flush()
    os.remove(fn)

  sys.stdout.write('Create new files.\n')
  sys.stdout.flush()
  if not os.path.isdir(path_prefix):
    os.makedirs(path_prefix)
  it = adict.iteritems()
  ii = 0
  while True:
    dt = dict(itertools.islice(it, split_into_n_each_file))
    ii += len(dt)
    if dt == {}:
      break
    else:
      ft = os.path.join(path_prefix, filename_prefix + '_' + str(uuid.uuid4()) + '.json')
      sys.stdout.write(
        'Creating file {} / {}: {:40}\n'.format(ii, len(adict), ft)
      )
      sys.stdout.flush()
      with open(ft, 'w') as fp:
        json.dump(dt, fp)


def split_list_and_write_into_json(alist, path_prefix, filename_prefix, split_into_n_each_file=1024):
  sys.stdout.write('Remove old files.\n')
  sys.stdout.flush()

  for fn in glob.glob(os.path.join(path_prefix, filename_prefix + '*.json')):
    sys.stdout.write('Removing file: {}.\n'.format(fn))
    sys.stdout.flush()
    os.remove(fn)

  sys.stdout.write('Create new files.\n')
  sys.stdout.flush()
  if not os.path.isdir(path_prefix):
    os.makedirs(path_prefix)
  it = iter(alist)
  ii = 0
  while True:
    lt = list(itertools.islice(it, split_into_n_each_file))
    ii += len(lt)
    if lt == []:
      break
    else:
      ft = os.path.join(path_prefix, filename_prefix + '_' + str(uuid.uuid4()) + '.json')
      sys.stdout.write(
        'Creating file {} / {}: {:40}\r'.format(ii, len(alist), ft)
      )
      sys.stdout.flush()
      with open(ft, 'w') as fp:
        json.dump(lt, fp)


