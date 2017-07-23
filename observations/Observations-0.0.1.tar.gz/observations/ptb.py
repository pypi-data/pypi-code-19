from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import os

from observations.util import maybe_download_and_extract


def ptb(path, as_words=True, as_integer=False):
  """Load the Penn Treebank data set (Marcus et al., 1993). The
  dataset is preprocessed and has a vocabulary of 10,000 words,
  including the end-of-sentence marker and a special symbol (<unk>)
  for rare words. There are 929,589 training words, 73,760 validation
  words, and 82,430 test words.

  Args:
    path: str.
      Path to directory which either stores file or otherwise file will
      be downloaded and stored there. Filenames are
      `simple-examples/data/ptb.train.txt`,
      `simple-examples/data/ptb.test.txt`,
      `simple-examples/data/ptb.valid.txt`.
    as_words: bool, optional.
      Whether to process data as list of words.
    as_integer: bool, optional.
      Whether to process each unique word as an integer.

  Returns:
    Tuple of str (if as_words=False) or lists
    `x_train, x_test, x_valid`.
  """
  path = os.path.expanduser(path)
  url = 'http://www.fit.vutbr.cz/~imikolov/rnnlm/simple-examples.tgz'
  maybe_download_and_extract(path, url)

  path = os.path.join(path, 'simple-examples/data')
  with open(os.path.join(path, 'ptb.train.txt')) as f:
    x_train = f.read().decode("utf-8").replace("\n", "<eos>")
  with open(os.path.join(path, 'ptb.test.txt')) as f:
    x_test = f.read().decode("utf-8").replace("\n", "<eos>")
  with open(os.path.join(path, 'ptb.valid.txt')) as f:
    x_valid = f.read().decode("utf-8").replace("\n", "<eos>")

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
