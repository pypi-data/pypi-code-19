from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import string

from observations.util import maybe_download_and_extract


def text8(path, as_words=False, as_integer=False):
  """Load the text8 data set (Mahoney, 2006). The
  dataset is preprocessed and has a vocabulary of 27 characters.
  There are 100 million characters.

  Args:
    path: str.
      Path to directory which either stores file or otherwise file will
      be downloaded and stored there. Filename is `text8.zip`.
    as_words: bool, optional.
      Whether to process data as list of words.
    as_integer: bool, optional.
      Whether to process each unique word as an integer.

  Returns:
    Tuple of str (if as_words=False) or lists
    `x_train, x_test, x_valid`.
  """
  path = os.path.expanduser(path)
  url = 'http://mattmahoney.net/dc/text8.zip'
  maybe_download_and_extract(path, url)
  with open(os.path.join(path, 'text8')) as f:
    text = f.read()
  x_train = text[:int(90e6)]
  x_test = text[int(95e6):int(100e6)]
  x_valid = text[int(90e6):int(95e6)]
  if as_words:
    x_train = x_train.split()
    x_test = x_test.split()
    x_valid = x_valid.split()
  if as_integer:
    vocab = string.ascii_lowercase + ' '
    char_to_int = dict(zip(vocab, range(len(vocab))))
    x_train = [char_to_int[char] for char in x_train if char in char_to_int]
    x_test = [char_to_int[char] for char in x_test if char in char_to_int]
    x_valid = [char_to_int[char] for char in x_valid if char in char_to_int]

  return x_train, x_test, x_valid
