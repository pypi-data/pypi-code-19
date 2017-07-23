from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import os

from observations.util import maybe_download_and_extract


def enwik8(path, as_words=False, as_integer=False):
  """Load enwik8 from the Hutter Prize (Hutter, 2012). The
  dataset is preprocessed and has a vocabulary of 205 characters.
  There are 100 million characters.

  Args:
    path: str.
      Path to directory which either stores file or otherwise file will
      be downloaded and stored there. Filename is `enwik8`.
    as_words: bool, optional.
      Whether to process data as list of words.
    as_integer: bool, optional.
      Whether to process each unique word as an integer.

  Returns:
    Tuple of str (if as_words=False) or lists
    `x_train, x_test, x_valid`.
  """
  path = os.path.expanduser(path)
  url = 'http://mattmahoney.net/dc/enwik8.zip'
  maybe_download_and_extract(path, url)
  with open(os.path.join(path, 'enwik8')) as f:
    text = f.read()
  x_train = text[:int(90e6)]
  x_test = text[int(95e6):int(100e6)]
  x_valid = text[int(90e6):int(95e6)]
  if as_words:
    x_train = x_train.split()
    x_test = x_test.split()
    x_valid = x_valid.split()
  if as_integer:
    counter = collections.Counter(x_train)
    count_pairs = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    words, _ = list(zip(*count_pairs))
    word_to_int = dict(zip(words, range(len(words))))
    x_train = [word_to_int[word] for word in x_train if word in word_to_int]
    x_test = [word_to_int[word] for word in x_test if word in word_to_int]
    x_valid = [word_to_int[word] for word in x_valid if word in word_to_int]

  return x_train, x_test, x_valid
