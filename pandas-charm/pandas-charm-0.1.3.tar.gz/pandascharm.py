#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas


__author__ = 'Markus Englund'
__license__ = 'MIT'
__version__ = '0.1.3'


def frame_as_categorical(frame, include_categories=None):
    """
    Return a pandas DataFrame with each column treated as a
    categorical with unordered categories. The same categories
    are applied to all columns.

    Parameters
    ----------
    frame : pandas.DataFrame
    include_categories : list (default: None)
        Categories to add unless they are already present
        in `frame`.
    """
    include_categories = include_categories if include_categories else []
    current_categories = pandas.unique(frame.values.ravel())
    current_categories_notnull = (
        current_categories[pandas.notnull(current_categories)])
    categories = set(current_categories_notnull).union(include_categories)
    categorical = frame.apply(lambda x: pandas.Series(x.astype('category')))
    unified_categorical = categorical.apply(
        lambda x: x.cat.set_categories(new_categories=categories))
    return unified_categorical


def frame_as_object(frame):
    """
    Return a pandas DataFrame as NumPy `dtype` ``object``.
    Useful for casting from a categorical frame.
    """
    return frame.apply(lambda x: x.astype('object'))


def from_bioalignment(bioalignment, categorical=True):
    """
    Convert a BioPython alignment to a pandas DataFrame.

    Parameters
    ----------
    bioalignment : Bio.Align.MultipleSeqAlignment
    categorical : bool (default: True)
        If True, the result will be returned as a categorical frame.
    """
    frame = pandas.DataFrame()
    dtype = 'category' if categorical else 'object'
    for record in bioalignment:
        s = pandas.Series(list(record.seq), name=record.id, dtype=dtype)
        frame = pandas.concat([frame, s], axis=1)
    return frame


def from_charmatrix(charmatrix, categorical=True):
    """
    Convert a DendroPy CharacterMatrix to a pandas DataFrame.

    Parameters
    ----------
    charmatrix : dendropy.CharacterMatrix
    categorical : bool (default: True)
        If True, the result will be returned as a categorical frame.
    """
    frame = pandas.DataFrame()
    for taxon, seq in charmatrix.items():
        s = pandas.Series(
            seq.symbols_as_list(), name=taxon.label)
        frame = pandas.concat([frame, s], axis=1)
    if categorical:
        state_alphabet = charmatrix.state_alphabets[0].symbols
        new_frame = frame_as_categorical(
            frame, include_categories=state_alphabet)
    else:
        new_frame = frame
    return new_frame


def to_bioalignment(frame, alphabet='generic_alphabet'):
    """
    Convert a pandas DataFrame to a BioPython MultipleSeqAlignment.

    Parameters
    ----------
    frame : pandas.DataFrame
    alphabet : str, default: 'generic_alignment'
        BioPython alphabet to use: 'generic_alphabet', 'generic_dna',
        'generic_nucleotide', 'generic_protein' or 'generic_rna')
    """
    if alphabet not in [
            'generic_alphabet', 'generic_dna',
            'generic_nucleotide', 'generic_protein', 'generic_rna']:
        raise ValueError(
            'Invalid BioPython alphabet: {}'
            .format(alphabet))
    try:
        import Bio.Alphabet
        from Bio.AlignIO import MultipleSeqAlignment
        from Bio.Seq import Seq
        from Bio.SeqRecord import SeqRecord
    except ImportError as ex:
        raise ImportError(
            '\'to_bioalignment\' requires BioPython.\n{ex}'.format(ex=str(ex)))
    alignment = MultipleSeqAlignment([])
    bio_alphabet = getattr(Bio.Alphabet, alphabet)
    for id, seq_series in frame.iteritems():
        seq_record = SeqRecord(
            Seq(''.join(seq_series), alphabet=bio_alphabet),
            id=id)
        alignment.append(seq_record)
    return alignment


def to_charmatrix(frame, data_type):
    """
    Convert a pandas DataFrame to a DendroPy CharacterMatrix.

    Parameters
    ----------
    frame : pandas.DataFrame
    data_type : str
        Type of CharacterMatrix to create: 'dna', 'rna',
        'protein' or 'standard'.
    """
    try:
        import dendropy
    except ImportError as ex:
        raise ImportError(
            '\'to_charmatrix\' requires DendroPy.\n{ex}'.format(ex=str(ex)))
    d = frame.apply(lambda x: ''.join(x), axis=0).to_dict()
    if data_type == 'standard':
        charmatrix = dendropy.StandardCharacterMatrix.from_dict(d)
    elif data_type == 'dna':
        charmatrix = dendropy.DnaCharacterMatrix.from_dict(d)
    elif data_type == 'rna':
        charmatrix = dendropy.RnaCharacterMatrix.from_dict(d)
    elif data_type == 'protein':
        charmatrix = dendropy.ProteinCharacterMatrix.from_dict(d)
    else:
        raise ValueError(
            '{} is not a valid data type'.format(repr(data_type)))
    # Preserve taxon name sort order
    taxon_names = list(frame.columns)
    charmatrix.taxon_namespace.sort(key=lambda x: taxon_names.index(x.label))
    return charmatrix
