from .iterator import VcfIterator
from .merger import VcfMerger


def iter_vcf(filename):
    import gzip
    with gzip.open(filename, 'rt', encoding='utf-8') if filename.endswith('.gz') else \
            open(filename, encoding='utf-8') as fileobj:
        iterator = VcfIterator(fileobj)
        yield from iterator
