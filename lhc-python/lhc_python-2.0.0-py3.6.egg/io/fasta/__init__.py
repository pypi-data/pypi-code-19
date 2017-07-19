import gzip

from .inorder_access_set import FastaInOrderAccessSet
from .iterator import FastaIterator, FastaFragmentIterator


def iter_fasta(filename):
    with gzip.open(filename, 'rt', encoding='utf-8') if filename.endswith('.gz') else \
            open(filename, encoding='utf-8') as fileobj:
        iterator = FastaIterator(fileobj)
        yield from iterator
