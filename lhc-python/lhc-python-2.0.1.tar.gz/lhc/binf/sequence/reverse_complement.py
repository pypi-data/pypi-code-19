REVERSE_COMPLEMENT_MAP = str.maketrans('acgtuwrkysmbhdvnACGTUWRKYSMBHDVN', 'tgcaawymrskvdhbnTGCAAWYMRSKVDHBN')


def reverse_complement(seq):
    return seq.translate(REVERSE_COMPLEMENT_MAP)[::-1]
