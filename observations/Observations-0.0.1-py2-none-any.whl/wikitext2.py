from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from observations.util import maybe_download_and_extract


def wikitext2(path, as_words=True):
  """Load the Wikitext-2 data set (Merity et al., 2016). The dataset
  is preprocessed and has a vocabulary of 33,278 words. There are
  2,088k training, 217k validation, and 245k test tokens.

  Args:
    path: str.
      Path to directory which either stores file or otherwise file will
      be downloaded and stored there. Filenames are
      `wikitext-2/wiki.train.tokens`,
      `wikitext-2/wiki.test.tokens`,
      `wikitext-2/wiki.valid.tokens`.
    as_words: bool, optional.
      Whether to process data as list of words.

  Returns:
    Tuple of str (if as_words=False) or lists `x_train, x_valid, x_test`.
  """
  path = os.path.expanduser(path)
  url = 'https://s3.amazonaws.com/research.metamind.io/wikitext/wikitext-2-v1.zip'
  maybe_download_and_extract(path, url)

  path = os.path.join(path, 'wikitext-2')
  with open(os.path.join(path, 'wiki.train.tokens')) as f:
    x_train = f.read().decode("utf-8")
  with open(os.path.join(path, 'wiki.test.tokens')) as f:
    x_test = f.read().decode("utf-8")
  with open(os.path.join(path, 'wiki.valid.tokens')) as f:
    x_valid = f.read().decode("utf-8")

  if as_words:
    x_train = x_train.split()
    x_test = x_test.split()
    x_valid = x_valid.split()

  return x_train, x_test, x_valid
