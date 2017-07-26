from lib.descriptors import ncomposition


def test_ncomposition_aacomposition():
    """ This is a basic test for ncomposition, testing the amino acid composition on a polypeptide consisting of
    10 alanines (A). It should return a vector with the first value of 1.0000 and the others as zero.

    :return:
    """
    STD_AMINO_ACIDS = [
        "A", "R", "N", "D", "C",
        "E", "Q", "G", "H", "I",
        "L", "K", "M", "F", "P",
        "S", "T", "W", "Y", "V"
    ]

    assert len(STD_AMINO_ACIDS) == 20

    alphabet = STD_AMINO_ACIDS
    kmerlen = 1
    round_to = 5
    fasta_seq = "AAAAAAAAAA"

    import itertools
    alphabet_list = sorted([''.join(kmer) for kmer in itertools.product(alphabet, repeat=kmerlen)])

    # This should return a vector of length 20
    vector = ncomposition(fasta_seq, alphabet_list, round_to)

    dummy_list = [str(round(0.0, round_to)) for kmer in alphabet]
    dummy_list[0] = str(round(1.0, round_to))

    assert len(vector) == 20
    assert vector == dummy_list


def test_ncomposition_dipeptidecomposition():
    pass


def test_physicochemical_properties():
    pass





